from __future__ import annotations

import json
import os
import re
from typing import Any

import streamlit as st
from openai import OpenAI

_BLOCKED_TERMS = {
    "none",
    "skill",
    "skills",
    "architecture",
    "control",
    "higher",
    "object",
    "pattern",
    "programming",
    "version",
    "backend",
    "apis",
    "api",
    "apis",
    "rest",
    "boot",
    "unit",
}

_ALLOWED_TECH_TERMS = {
    "java",
    "python",
    "sql",
    "mysql",
    "postgresql",
    "oracle",
    "mongodb",
    "redis",
    "spring",
    "spring boot",
    "spring mvc",
    "microservices",
    "microservices architecture",
    "rest api",
    "restful api",
    "docker",
    "kubernetes",
    "git",
    "github",
    "jenkins",
    "cicd",
    "junit",
    "unit testing",
    "oop",
}

_TECH_VOCAB = {
    "java",
    "python",
    "sql",
    "mysql",
    "postgresql",
    "oracle",
    "mongodb",
    "redis",
    "spring",
    "spring boot",
    "spring mvc",
    "spring data",
    "spring security",
    "microservices",
    "microservices architecture",
    "rest api",
    "restful api",
    "docker",
    "kubernetes",
    "git",
    "github",
    "jenkins",
    "cicd",
    "junit",
    "unit testing",
    "oop",
    "nosql",
    "aws",
    "azure",
    "gcp",
    "kafka",
    "rabbitmq",
}

_SKILL_FAMILIES = [
    {"sql", "mysql", "postgresql", "oracle"},
    {"nosql", "mongodb", "redis"},
    {"spring", "spring boot", "spring mvc", "spring data", "spring security"},
    {"rest api", "restful api"},
    {"unit testing", "junit"},
    {"microservices", "microservices architecture"},
]


def _get_api_key() -> str:
    return st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))


def _is_technical_phrase(skill: str, baseline_pool: set[str]) -> bool:
    if not skill:
        return False
    s = skill.strip().lower()
    if not s or s in _BLOCKED_TERMS:
        return False
    if len(s) < 2 or re.fullmatch(r"\d+", s):
        return False
    if s in _ALLOWED_TECH_TERMS:
        return True
    if " " in s and any(tok in _ALLOWED_TECH_TERMS for tok in s.split()):
        return True
    # Keep baseline terms only when they have strong technical anchors.
    if s in baseline_pool and any(
        anchor in s
        for anchor in (
            "java",
            "python",
            "sql",
            "mysql",
            "oracle",
            "mongo",
            "redis",
            "spring",
            "microservice",
            "docker",
            "kubernetes",
            "git",
            "jenkins",
            "junit",
            "testing",
            "aws",
            "azure",
            "gcp",
            "kafka",
            "rabbitmq",
        )
    ):
        return True
    return False


def _sanitize_skills(skills: list[Any], baseline_pool: set[str]) -> list[str]:
    clean: list[str] = []
    for item in skills:
        if not isinstance(item, str):
            continue
        s = item.strip().lower()
        if _is_technical_phrase(s, baseline_pool):
            clean.append(s)
    return list(dict.fromkeys(clean))


def _normalize_text_for_match(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _skill_variants(skill: str) -> list[str]:
    s = skill.strip().lower()
    variants = {s, s.replace(" ", "")}
    if s == "cicd":
        variants.update({"ci cd", "ci/cd", "ci-cd"})
    if s == "rest api":
        variants.update({"restful api", "rest apis"})
    if s == "spring boot":
        variants.update({"springboot"})
    if s == "unit testing":
        variants.update({"unit test", "junit"})
    return sorted(v for v in variants if v)


def _contains_skill(text_norm: str, skill: str) -> bool:
    for v in _skill_variants(skill):
        v_norm = _normalize_text_for_match(v)
        if not v_norm:
            continue
        if f" {v_norm} " in f" {text_norm} ":
            return True
    return False


def _extract_skills_from_text(text_norm: str) -> list[str]:
    found: list[str] = []
    for skill in sorted(_TECH_VOCAB, key=len, reverse=True):
        if _contains_skill(text_norm, skill):
            found.append(skill)
    return list(dict.fromkeys(found))


def _family_members(skill: str) -> set[str]:
    s = skill.strip().lower()
    members = {s}
    for fam in _SKILL_FAMILIES:
        if s in fam:
            members |= fam
    return members


def _deterministic_recheck(merged: dict[str, Any], raw_text: dict[str, str]) -> dict[str, Any]:
    syllabus_norm = _normalize_text_for_match(raw_text.get("syllabus_text", ""))
    jd_norm = _normalize_text_for_match(raw_text.get("jd_text", ""))
    if not syllabus_norm or not jd_norm:
        return merged

    jd_candidates = merged.get("jd_top_skills", []) or []
    baseline_pool = {
        str(x).strip().lower()
        for key in ("jd_top_skills", "matching_skills", "missing_skills", "good_matches", "partial_matches")
        for x in merged.get(key, [])
        if isinstance(x, str)
    }
    jd_from_baseline = [s for s in _sanitize_skills(jd_candidates, baseline_pool) if s != "none"]
    jd_from_raw = _extract_skills_from_text(jd_norm)
    jd_skills = list(dict.fromkeys(jd_from_baseline + jd_from_raw))
    if not jd_skills:
        return merged

    strong: list[str] = []
    partial: list[str] = []
    weak: list[str] = []
    missing: list[str] = []

    for skill in jd_skills:
        in_syllabus = _contains_skill(syllabus_norm, skill)
        in_jd = _contains_skill(jd_norm, skill)
        if not in_jd:
            continue
        if in_syllabus:
            # Frequency-based confidence: repeated mention => strong.
            base = _normalize_text_for_match(skill)
            freq = syllabus_norm.count(base)
            if freq >= 2:
                strong.append(skill)
            else:
                weak.append(skill)
        else:
            # Family-aware soft match (e.g., sql/mysql, spring/spring boot, junit/unit testing).
            fam_hit = any(_contains_skill(syllabus_norm, member) for member in _family_members(skill))
            # Partial when at least one token appears in syllabus context.
            tokens = [t for t in skill.split() if len(t) > 2 and t not in _BLOCKED_TERMS]
            token_hit = tokens and any(f" {t} " in f" {syllabus_norm} " for t in tokens)
            if fam_hit:
                weak.append(skill)
            elif token_hit:
                partial.append(skill)
            else:
                missing.append(skill)

    # De-dup by priority.
    seen = set()
    strong = [x for x in strong if not (x in seen or seen.add(x))]
    partial = [x for x in partial if x not in seen and not seen.add(x)]
    weak = [x for x in weak if x not in seen and not seen.add(x)]
    missing = [x for x in missing if x not in seen and not seen.add(x)]

    if strong or partial or weak or missing:
        merged["strong_match"] = strong
        merged["partial_match"] = partial
        merged["weak_match"] = weak
        merged["missing_skills"] = missing
        merged["good_matches"] = strong
        merged["partial_matches"] = partial + weak
        merged["matching_skills"] = strong + partial + weak
    return merged


def _normalize_verified_result(baseline_results: dict[str, Any], verified: dict[str, Any]) -> dict[str, Any]:
    baseline_pool = {
        str(x).strip().lower()
        for key in ("jd_top_skills", "syllabus_top_skills", "matching_skills", "missing_skills", "good_matches", "partial_matches")
        for x in baseline_results.get(key, [])
        if isinstance(x, str)
    }

    strong_raw = verified.get("strong_match", []) or baseline_results.get("good_matches", [])
    partial_raw = verified.get("partial_match", []) or baseline_results.get("partial_matches", [])
    weak_raw = verified.get("weak_match", [])
    missing_raw = verified.get("missing_skills", []) or baseline_results.get("missing_skills", [])

    strong = _sanitize_skills(strong_raw, baseline_pool)
    partial = _sanitize_skills(partial_raw, baseline_pool)
    weak = _sanitize_skills(weak_raw, baseline_pool)
    missing = _sanitize_skills(missing_raw, baseline_pool)

    # Strong > partial > weak > missing (dedupe across categories by priority).
    seen = set(strong)
    partial = [x for x in partial if x not in seen]
    seen.update(partial)
    weak = [x for x in weak if x not in seen]
    seen.update(weak)
    missing = [x for x in missing if x not in seen]

    # Preserve existing keys for backwards compatibility with current UI/reporting.
    merged = dict(baseline_results)
    merged["strong_match"] = list(dict.fromkeys(strong))
    merged["partial_match"] = list(dict.fromkeys(partial))
    merged["weak_match"] = list(dict.fromkeys(weak))
    merged["missing_skills"] = list(dict.fromkeys(missing))
    merged["good_matches"] = merged["strong_match"]
    merged["partial_matches"] = list(dict.fromkeys(merged["partial_match"] + merged["weak_match"]))
    merged["matching_skills"] = list(dict.fromkeys(merged["good_matches"] + merged["partial_matches"]))
    return merged


@st.cache_data(show_spinner=False)
def _cached_verify(baseline_results: dict[str, Any], raw_text: dict[str, str]) -> dict[str, Any]:
    api_key = _get_api_key()
    if not api_key:
        return baseline_results

    client = OpenAI(api_key=api_key)
    syllabus_text = raw_text.get("syllabus_text", "")
    jd_text = raw_text.get("jd_text", "")
    payload = {
        "baseline_results": baseline_results,
        "syllabus_text": syllabus_text[:16000],
        "jd_text": jd_text[:16000],
    }

    prompt = (
        "You are a strict verifier for curriculum-vs-job skill mapping.\n"
        "Given baseline NLP output and source text, fix missed synonyms, miscategorized skills, and weak categorization.\n"
        "Return only valid JSON with keys: strong_match, partial_match, weak_match, missing_skills.\n"
        "Rules:\n"
        "- strong_match: direct and explicit skill matches in both texts.\n"
        "- partial_match: concept exists in syllabus but lacks depth, tools, or specificity.\n"
        "- weak_match: vague mention only; substantial upskilling needed.\n"
        "- missing_skills: critical JD skills absent from syllabus.\n"
        "- No duplicates. Keep concise, skill-oriented phrases only."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": f"{prompt}\n\nInput:\n{json.dumps(payload)}"},
            ],
            timeout=8,
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        return _normalize_verified_result(baseline_results, parsed if isinstance(parsed, dict) else {})
    except Exception:
        return baseline_results


def verify_results(baseline_results: dict[str, Any], raw_text: dict[str, str]) -> dict[str, Any]:
    """Silently upgrades baseline output. Falls back to baseline on failure."""
    try:
        merged = _cached_verify(baseline_results, raw_text)
        return _deterministic_recheck(merged, raw_text)
    except Exception:
        return _deterministic_recheck(dict(baseline_results), raw_text)


@st.cache_data(show_spinner=False)
def _cached_resume_markdown(selected_role: str, student_data: str, analysis_result: dict[str, Any]) -> str:
    api_key = _get_api_key()
    strong = analysis_result.get("strong_match", []) or analysis_result.get("good_matches", [])
    partial = analysis_result.get("partial_match", []) or analysis_result.get("partial_matches", [])
    missing = analysis_result.get("missing_skills", [])

    fallback = (
        f"# {selected_role} Resume\n\n"
        "## Profile\n"
        f"{student_data.strip() or 'Student profile pending.'}\n\n"
        "## Core Strengths\n"
        + ("\n".join(f"- {s}" for s in strong[:12]) if strong else "- Building foundational skills")
        + "\n\n## Projects\n- Add 2-3 role-aligned projects here.\n\n"
        "## Learning Path\n"
        + ("\n".join(f"- {s}" for s in (partial + missing)[:12]) if (partial or missing) else "- Continue advanced specialization")
    )
    if not api_key:
        return fallback

    client = OpenAI(api_key=api_key)
    prompt = (
        f"Act as a professional technical recruiter. Create a resume for a {selected_role} "
        "based on this student's data. Focus on their 'Strong Match' skills. For 'Missing' or "
        "'Partial' skills, list them under a section titled 'Learning Path' or 'Current Certifications' "
        "to show progress. If student_data is empty, generate a strong fresher-style role-focused resume "
        "using the analysis_result as truth and add realistic beginner projects. Return markdown only."
    )
    payload = {
        "student_data": student_data[:5000],
        "analysis_result": {
            "strong_match": strong,
            "partial_match": partial,
            "missing_skills": missing,
        },
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You write concise ATS-friendly technical resumes in markdown."},
                {"role": "user", "content": f"{prompt}\n\nInput:\n{json.dumps(payload)}"},
            ],
            timeout=25,
        )
        return (response.choices[0].message.content or "").strip() or fallback
    except Exception:
        return fallback


def generate_resume_markdown(selected_role: str, student_data: str, analysis_result: dict[str, Any]) -> str:
    try:
        return _cached_resume_markdown(selected_role, student_data, analysis_result)
    except Exception:
        strong = analysis_result.get("strong_match", []) or analysis_result.get("good_matches", [])
        partial = analysis_result.get("partial_match", []) or analysis_result.get("partial_matches", [])
        missing = analysis_result.get("missing_skills", [])
        return (
            f"# {selected_role} Resume\n\n"
            "## Profile\n"
            f"{student_data.strip() or 'Student profile pending.'}\n\n"
            "## Core Strengths\n"
            + ("\n".join(f"- {s}" for s in strong[:12]) if strong else "- Building foundational skills")
            + "\n\n## Learning Path\n"
            + (
                "\n".join(f"- {s}" for s in (partial + missing)[:12])
                if (partial or missing)
                else "- Continue advanced specialization"
            )
        )
