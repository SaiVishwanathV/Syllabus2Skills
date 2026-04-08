"""
Core NLP utilities for text normalization and token processing.
"""

from __future__ import annotations

import re
import ssl
from typing import List

import nltk
import streamlit as st
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_lemmatizer = WordNetLemmatizer()
EXTRA_STOPWORDS = {
    # Common pattern that pollutes keyword extraction (e.g., "using java").
    "using",
    # A couple of frequent "non-skill" verbs that often appear before skills.
    "use",
    "used",
    # Generic non-skill wording that often pollutes "skills" lists
    "experience",
    "experienced",
    "year",
    "years",
    "strong",
    "knowledge",
    "familiarity",
    "familiar",
    "preferred",
    "excellent",
    "understanding",
    "understand",
    "understandings",
    "skill",
    "skills",
    "hands",
    "handson",
    "hands-on",
    "proficiency",
    "proficient",
    "problem",
    "solving",
    "debugging",
    "performance",
    "tuning",
    "ability",
    "good",
    "great",
    "including",
    "etc",
    "such",
    "like",
    "preferred",
    "writing",
    "develop",
    "developing",
    "design",
    "designing",
    "work",
    "working",
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


def get_stopword_set() -> set[str]:
    """
    Stopwords set used across the app.

    We prefer NLTK stopwords when available, but fall back to scikit-learn's list
    plus project-specific extras.
    """
    try:
        sw = set(stopwords.words("english"))
    except LookupError:
        sw = set(ENGLISH_STOP_WORDS)
    return sw.union(EXTRA_STOPWORDS)


@st.cache_resource(show_spinner=False)
def ensure_nltk_resources() -> None:
    """
    Download required NLTK resources.
    Safe to call repeatedly.
    """
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    resources = [
        ("corpora/stopwords", "stopwords"),
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/wordnet", "wordnet"),
    ]
    for path, package in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(package, quiet=True)


def clean_text(text: str) -> str:
    """
    Lowercase and keep only alphanumeric/whitespace characters.
    """
    lowered = text.lower().strip()

    # Normalize CI/CD variants so they don't become separate "ci", "cd", "ci cd".
    # Examples handled: "CI/CD", "CI-CD", "CI CD"
    lowered = re.sub(r"\bci\s*[/\-\s]*cd\b", "cicd", lowered)

    no_special = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return re.sub(r"\s+", " ", no_special).strip()


def tokenize_text(text: str) -> List[str]:
    """
    Tokenize text with punctuation already removed by clean_text.
    """
    normalized = clean_text(text)
    if not normalized:
        return []
    try:
        return word_tokenize(normalized)
    except LookupError:
        # Fallback when punkt resources are unavailable.
        return re.findall(r"[a-z0-9]+", normalized)


def lemmatize_tokens(tokens: List[str], remove_stopwords: bool = True) -> List[str]:
    """
    Lemmatize tokens and optionally remove English stopwords.
    """
    filtered = tokens
    if remove_stopwords:
        stop_words = get_stopword_set()
        filtered = [token for token in tokens if token not in stop_words]
    output: list[str] = []
    for token in filtered:
        if not token.strip():
            continue
        try:
            output.append(_lemmatizer.lemmatize(token))
        except LookupError:
            output.append(token)
    return output


def preprocess_text(text: str) -> List[str]:
    """
    Full text processing pipeline used by analysis modules.
    """
    return lemmatize_tokens(tokenize_text(text), remove_stopwords=True)
