"""
Lightweight skill-strength classifier.

We train a small logistic regression model on synthetic data so we can consistently
label matched skills as STRONG vs WEAK based on:
- raw frequency in syllabus/resume text
- TF-IDF weight in syllabus/resume vs JD
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression


@dataclass(frozen=True)
class SkillStrengthPrediction:
    label: str  # "strong" or "weak"
    confidence: float  # probability of "strong"


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


import os
import pandas as pd

def train_strength_model(seed: int = 42) -> LogisticRegression:
    dataset_path = "skill_match_dataset.csv"

    if os.path.exists(dataset_path):
        # Load from the physical dataset if it exists!
        df = pd.read_csv(dataset_path)
        X = df[["log_freq", "syllabus_tfidf", "jd_tfidf", "ratio"]].values
        y = df["is_strong_match"].values
    else:
        # Generate the dataset and save it to a CSV file
        rng = np.random.default_rng(seed)
        n = 4000
    
        freq = rng.integers(0, 8, size=n)
        syl = rng.random(n) ** 1.2
        jd = rng.random(n) ** 1.1
        ratio = syl / (jd + 1e-6)
    
        X = np.column_stack([np.log1p(freq), syl, jd, ratio])
    
        base = (
            1.2 * (np.log1p(freq) - 0.7)
            + 1.6 * (syl - 0.25)
            + 0.8 * (ratio - 0.45)
            - 0.4 * (jd - 0.6)
        )
        p_strong = 1.0 / (1.0 + np.exp(-base))
        y = (rng.random(n) < p_strong).astype(int)
        
        # Save mapping to CSV so the user can submit the physical dataset
        df = pd.DataFrame(X, columns=["log_freq", "syllabus_tfidf", "jd_tfidf", "ratio"])
        df["is_strong_match"] = y
        df.to_csv(dataset_path, index=False)

    model = LogisticRegression(max_iter=500)
    model.fit(X, y)
    return model


_MODEL: LogisticRegression | None = None


def get_strength_model() -> LogisticRegression:
    global _MODEL
    if _MODEL is None:
        _MODEL = train_strength_model()
    return _MODEL


def predict_strength(*, freq: int, syllabus_tfidf: float, jd_tfidf: float) -> SkillStrengthPrediction:
    model = get_strength_model()
    ratio = float(syllabus_tfidf) / (float(jd_tfidf) + 1e-6)
    X = np.array([[math.log1p(max(freq, 0)), float(syllabus_tfidf), float(jd_tfidf), ratio]])
    proba_strong = float(model.predict_proba(X)[0][1])
    label = "strong" if proba_strong >= 0.6 else "weak"
    return SkillStrengthPrediction(label=label, confidence=proba_strong)

