"""
Skill gap analysis engine:
- TF-IDF feature extraction
- Cosine similarity
- Skill Gap Index (SGI)
- Keyword matching for missing/matching skills
"""

from __future__ import annotations

from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.nlp_utils import get_stopword_set, preprocess_text
from utils.skill_strength_model import predict_strength
from utils.openai_filter import filter_technical_skills


def _safe_join(tokens: list[str]) -> str:
    return " ".join(tokens) if tokens else ""


def _ngram_counts(tokens: list[str], n: int) -> Counter[str]:
    if n <= 1:
        return Counter(tokens)
    if len(tokens) < n:
        return Counter()
    grams = [" ".join(tokens[i : i + n]) for i in range(0, len(tokens) - n + 1)]
    return Counter(grams)


def _canonicalize(tokens: list[str], stop_words: set[str]) -> str:
    """
    Canonicalize a TF-IDF feature into a display/matchable "skill" token.

    Examples:
    - ["using","java"] -> "java"
    - ["ci","cd"] -> "cicd"
    """
    tokens = [t.strip() for t in tokens if t.strip()]
    if not tokens:
        return ""

    if len(tokens) == 1:
        return "" if tokens[0] in stop_words else tokens[0]

    # Merge known constructs
    if len(tokens) == 2 and tokens[0] == "ci" and tokens[1] == "cd":
        return "cicd"

    if all(t in stop_words for t in tokens):
        return ""

    # Drop leading stopword/connector for common patterns like "using java"
    if len(tokens) == 2 and tokens[0] in stop_words:
        if tokens[1] not in stop_words:
            return tokens[1]

    return " ".join(tokens)


_DISALLOWED_SKILLS = {
    # Generic wording that should never be treated as skills
    "experience",
    "strong",
    "knowledge",
    "familiarity",
    "preferred",
    "excellent",
    "understanding",
    "skills",
    "skill",
    "problem",
    "solving",
    "debugging",
    "performance",
    "tuning",
    "designing",
    "developing",
    "design",
    "develop",
    "work",
    "working",
    "ability",
    "good",
    "great",
    "etc",
    "such",
    "like",
    "including",
    "beginner",
    "willingness",
    "willing",
    "eager",
    "eagerness",
    "learn",
    "learning",
    "passion",
    "passionate",
    "motivated",
    "motivation",
    "drive",
    "driven",
    "enthusiastic",
    "enthusiasm",
    "proven",
    "track",
    "record",
    "highly",
    "plus",
    "basic",
    "advanced",
    "expert",
    "level",
    "understanding",
    "bonus",
    "curiosity",
    "collaborative",
    "effectively",
    "interest",
    "interpersonal",
    "capability",
    "communication",
    "environment",
    "framework",
    "logical",
    "new",
    "oriented",
    "software",
    "solution",
    "solutions",
    "team",
    "technology",
    "technologies",
    "thinking",
    # Additional generic JD terms
    "business",
    "engineer",
    "system",
    "systems",
    "development",
    "tool",
    "tools",
    "engineering",
    "pipeline",
    "pipelines",
    "job",
    "service",
    "services",
    "process",
    "processes",
    "build",
    "analytics",
    "project",
    "projects",
    "client",
    "clients",
    "experience",
    "year",
    "years",
    "management",
    "requirement",
    "requirements",
    "support",
    "design",
    "using",
    "required",
    "role",
    "ensure",
    "knowledge",
    "ability",
    "strong",
    "working",
    "work",
    "data",
}

_ALLOWED_PHRASES = {
    # Frameworks / Java ecosystem
    "spring boot",
    "spring mvc",
    "spring data",
    "spring security",
    "microservices architecture",
    "rest api",
    "restful api",
    "web services",
    # Databases
    "mysql",
    "mongodb",
    "redis",
    "nosql",
    # Cloud
    "aws",
    "azure",
    "gcp",
    # DevOps
    "docker",
    "kubernetes",
    "cicd",
    "jenkins",
    "github actions",
    "gitlab cicd",
    # Messaging
    "kafka",
    "rabbitmq",
    "activemq",
    # Testing
    "junit",
    "mockito",
    "unit testing",
    # Concepts
    "multithreading",
    "concurrency",
    "memory management",
    "json",
    "sql",
    "java",
}


def _is_candidate_skill(term: str, stop_words: set[str]) -> bool:
    if not term:
        return False
    if term in stop_words:
        return False
    if term in _DISALLOWED_SKILLS:
        return False
    if term.isdigit():
        return False
    if len(term) <= 1:
        return False
    return True


def analyze_gap(syllabus_text: str, jd_text: str, top_k: int = 25) -> dict:
    syllabus_tokens = preprocess_text(syllabus_text)
    jd_tokens = preprocess_text(jd_text)

    syllabus_clean = _safe_join(syllabus_tokens)
    jd_clean = _safe_join(jd_tokens)

    if not syllabus_clean or not jd_clean:
        return {
            "cosine_similarity": 0.0,
            "skill_gap_index_cosine": 100.0,
            "skill_gap_index": 100.0,
            "jd_top_skills": [],
            "missing_skills": [],
            "matching_skills": [],
            "good_matches": [],
            "partial_matches": [],
            "syllabus_top_skills": [],
            "syllabus_clean_text": syllabus_clean,
            "jd_clean_text": jd_clean,
        }

    # Use a higher-order vector space for cosine similarity (global alignment),
    # but keep keyword extraction focused on unigrams for precision.
    try:
        vectorizer_cosine = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        matrix_cosine = vectorizer_cosine.fit_transform([syllabus_clean, jd_clean])
        cosine_score = float(cosine_similarity(matrix_cosine[0:1], matrix_cosine[1:2])[0][0])
    except ValueError:
        cosine_score = 0.0
    sgi_cosine = (1.0 - cosine_score) * 100.0

    stop_words = get_stopword_set()

    # Create n-gram match structures from preprocessed tokens.
    syllabus_unigram_counts = _ngram_counts(syllabus_tokens, 1)
    syllabus_bigram_counts = _ngram_counts(syllabus_tokens, 2)
    syllabus_unigrams = set(syllabus_unigram_counts.keys())
    syllabus_bigrams = set(syllabus_bigram_counts.keys())

    def is_in_syllabus(canon: str) -> bool:
        if not canon:
            return False
        if " " in canon:
            return canon in syllabus_bigrams
        return canon in syllabus_unigrams

    def score_to_canon_dict(
        *,
        vector: list[float],
        feature_names_local: list[str],
    ) -> dict[str, float]:
        scored: dict[str, float] = {}
        # Consider more than top_k because multiple features can canonicalize to one term.
        candidates = [(i, float(vector[i])) for i in range(len(vector)) if vector[i] > 0]
        candidates.sort(key=lambda x: x[1], reverse=True)
        for idx, score in candidates[: max(top_k * 4, 30)]:
            term = feature_names_local[idx]
            term_tokens = term.split()
            canon = _canonicalize(term_tokens, stop_words)
            if not canon:
                continue
            if not _is_candidate_skill(canon, stop_words):
                continue
            scored[canon] = scored.get(canon, 0.0) + score
        return scored

    try:
        vectorizer_kw = TfidfVectorizer(ngram_range=(1, 1), min_df=1)
        matrix_kw = vectorizer_kw.fit_transform([syllabus_clean, jd_clean])
        kw_feature_names = vectorizer_kw.get_feature_names_out()

        jd_vector_kw = matrix_kw[1].toarray().flatten()
        syllabus_vector_kw = matrix_kw[0].toarray().flatten()
    except ValueError:
        kw_feature_names = []
        jd_vector_kw = []
        syllabus_vector_kw = []

    # For strength scoring, keep a quick lookup from unigram -> tfidf in each document.
    jd_tfidf_by_token = {kw_feature_names[i]: float(jd_vector_kw[i]) for i in range(len(kw_feature_names))}
    syllabus_tfidf_by_token = {kw_feature_names[i]: float(syllabus_vector_kw[i]) for i in range(len(kw_feature_names))}

    jd_weights_by_canon = score_to_canon_dict(
        vector=jd_vector_kw, feature_names_local=kw_feature_names
    )
    syllabus_weights_by_canon = score_to_canon_dict(
        vector=syllabus_vector_kw, feature_names_local=kw_feature_names
    )

    # Add phrase-level skills based on preprocessed token n-grams.
    jd_bigram_counts = _ngram_counts(jd_tokens, 2)
    jd_trigram_counts = _ngram_counts(jd_tokens, 3)

    def _bump_phrase(phrase: str, amount: float) -> None:
        if not phrase:
            return
        jd_weights_by_canon[phrase] = jd_weights_by_canon.get(phrase, 0.0) + amount

    for phrase in _ALLOWED_PHRASES:
        if " " in phrase:
            if phrase.count(" ") == 1 and jd_bigram_counts.get(phrase, 0) > 0:
                _bump_phrase(phrase, 1.0)
            elif phrase.count(" ") == 2 and jd_trigram_counts.get(phrase, 0) > 0:
                _bump_phrase(phrase, 1.0)
        else:
            # single tokens already handled by TF-IDF; keep only if present in JD
            if phrase in set(jd_tokens):
                _bump_phrase(phrase, 0.5)

    jd_ranked = sorted(jd_weights_by_canon.items(), key=lambda kv: kv[1], reverse=True)
    raw_top_jd_canon_terms = [k for k, _ in jd_ranked[: max(top_k * 3, 60)]]
    
    # Secure OpenAI skill purification
    top_jd_canon_terms_all = filter_technical_skills(raw_top_jd_canon_terms)
    top_jd_canon_terms = top_jd_canon_terms_all[:top_k]

    total_weight = sum(jd_weights_by_canon.get(t, 0.0) for t in top_jd_canon_terms)
    matched_weight = sum(
        jd_weights_by_canon.get(t, 0.0) for t in top_jd_canon_terms if is_in_syllabus(t)
    )
    coverage = (matched_weight / total_weight) if total_weight > 0 else 0.0
    sgi_weighted = (1.0 - coverage) * 100.0

    missing_skills = [t for t in top_jd_canon_terms if not is_in_syllabus(t)]
    matching_skills = [t for t in top_jd_canon_terms if is_in_syllabus(t)]

    # Strength scoring for matched skills (strong/weak + confidence).
    skill_strength: dict[str, dict] = {}
    for skill in matching_skills:
        if " " in skill:
            freq = int(syllabus_bigram_counts.get(skill, 0))
            syl_tfidf = 0.0
            jd_tfidf = 0.0
        else:
            freq = int(syllabus_unigram_counts.get(skill, 0))
            syl_tfidf = float(syllabus_tfidf_by_token.get(skill, 0.0))
            jd_tfidf = float(jd_tfidf_by_token.get(skill, 0.0))

        pred = predict_strength(freq=freq, syllabus_tfidf=syl_tfidf, jd_tfidf=jd_tfidf)
        skill_strength[skill] = {
            "label": pred.label,
            "confidence": round(pred.confidence, 3),
            "freq": freq,
            "syllabus_tfidf": round(syl_tfidf, 4),
            "jd_tfidf": round(jd_tfidf, 4),
        }

    # Split matching into "good" (stronger repetition) vs "partial" (weaker presence).
    good_matches: list[str] = []
    partial_matches: list[str] = []
    for skill in matching_skills:
        label = skill_strength.get(skill, {}).get("label", "weak")
        (good_matches if label == "strong" else partial_matches).append(skill)

    syllabus_ranked = sorted(
        syllabus_weights_by_canon.items(), key=lambda kv: kv[1], reverse=True
    )
    raw_top_syllabus_canon_terms = [k for k, _ in syllabus_ranked[: max(top_k * 3, 60)]]
    top_syllabus_canon_terms_all = filter_technical_skills(raw_top_syllabus_canon_terms)
    top_syllabus_canon_terms = top_syllabus_canon_terms_all[:top_k]

    return {
        "cosine_similarity": round(cosine_score, 4),
        "skill_gap_index_cosine": round(sgi_cosine, 2),
        "skill_gap_index": round(sgi_weighted, 2),
        "jd_top_skills": top_jd_canon_terms,
        "missing_skills": missing_skills,
        "matching_skills": matching_skills,
        "good_matches": good_matches,
        "partial_matches": partial_matches,
        "skill_strength": skill_strength,
        "syllabus_top_skills": top_syllabus_canon_terms,
        "syllabus_clean_text": syllabus_clean,
        "jd_clean_text": jd_clean,
    }


def predictive_suggestions(missing_skills: list[str], limit: int = 8) -> list[str]:
    if not missing_skills:
        return [
            "Maintain alignment by adding advanced projects and assessment rubrics.",
            "Track market trends quarterly and refresh curriculum outcomes.",
        ]
    unique = list(dict.fromkeys(missing_skills))[:limit]
    return [
        f"Add a focused module or lab for '{skill}'."
        for skill in unique
    ]
