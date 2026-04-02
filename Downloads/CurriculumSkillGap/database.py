"""
Supabase persistence layer for user accounts and analysis reports.

Replaces the previous SQLite/SQLAlchemy implementation.
The public API (function signatures) is identical, so no other file needs changing.

Supabase tables required (run once in the SQL editor):
─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            BIGSERIAL PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name  TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reports (
    id                   BIGSERIAL PRIMARY KEY,
    user_id              BIGINT REFERENCES users(id) ON DELETE CASCADE,
    timestamp            TIMESTAMPTZ DEFAULT NOW(),
    analysis_type        TEXT NOT NULL DEFAULT 'syllabus_vs_jd',
    syllabus_name        TEXT NOT NULL,
    jd_role              TEXT NOT NULL,
    cosine_similarity    FLOAT NOT NULL,
    gap_index_score      FLOAT NOT NULL,
    missing_skills_json  TEXT NOT NULL,
    matching_skills_json TEXT NOT NULL
);
─────────────────────────────────────────────────────
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from supabase_client import get_supabase


# ---------------------------------------------------------------------------
# Lightweight data-classes that mirror the old SQLAlchemy ORM objects.
# This keeps the pages (Dashboard, History, etc.) working without changes.
# ---------------------------------------------------------------------------

@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    display_name: str
    created_at: datetime


@dataclass
class Report:
    id: int
    user_id: int
    timestamp: datetime
    analysis_type: str
    syllabus_name: str
    jd_role: str
    cosine_similarity: float
    gap_index_score: float
    missing_skills_json: str
    matching_skills_json: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_dt(value: str | None) -> datetime:
    """Convert a Supabase ISO-8601 timestamp string to a datetime object."""
    if not value:
        return datetime.utcnow()
    # Supabase returns e.g. "2024-01-15T12:34:56.789Z" or "+00:00" suffix
    value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.utcnow()


def _row_to_user(row: dict) -> User:
    return User(
        id=row["id"],
        username=row["username"],
        email=row["email"],
        password_hash=row["password_hash"],
        display_name=row["display_name"],
        created_at=_parse_dt(row.get("created_at")),
    )


def _row_to_report(row: dict) -> Report:
    return Report(
        id=row["id"],
        user_id=row["user_id"],
        timestamp=_parse_dt(row.get("timestamp")),
        analysis_type=row.get("analysis_type", "syllabus_vs_jd"),
        syllabus_name=row.get("syllabus_name", ""),
        jd_role=row.get("jd_role", ""),
        cosine_similarity=float(row.get("cosine_similarity", 0.0)),
        gap_index_score=float(row.get("gap_index_score", 0.0)),
        missing_skills_json=row.get("missing_skills_json", "[]"),
        matching_skills_json=row.get("matching_skills_json", "[]"),
    )


def _get_user_id(username: str) -> Optional[int]:
    """Return the integer user id for a given username, or None."""
    sb = get_supabase()
    res = sb.table("users").select("id").eq("username", username).execute()
    if res.data:
        return res.data[0]["id"]
    return None


# ---------------------------------------------------------------------------
# No-op kept for backwards compatibility (tables are created in Supabase UI)
# ---------------------------------------------------------------------------

def init_db() -> None:  # noqa: D401
    """No-op. Tables are created once via the Supabase SQL editor."""


# ---------------------------------------------------------------------------
# User existence checks
# ---------------------------------------------------------------------------

def username_exists(username: str) -> bool:
    sb = get_supabase()
    res = sb.table("users").select("id").eq("username", username).execute()
    return bool(res.data)


def email_exists(email: str) -> bool:
    sb = get_supabase()
    res = sb.table("users").select("id").eq("email", email).execute()
    return bool(res.data)


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

def create_user(
    *,
    username: str,
    email: str,
    password_hash: str,
    display_name: str,
) -> None:
    sb = get_supabase()
    sb.table("users").insert(
        {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "display_name": display_name,
        }
    ).execute()


def get_user_by_username(username: str) -> Optional[User]:
    sb = get_supabase()
    res = sb.table("users").select("*").eq("username", username).execute()
    if res.data:
        return _row_to_user(res.data[0])
    return None


# ---------------------------------------------------------------------------
# Report CRUD
# ---------------------------------------------------------------------------

def create_report(
    *,
    username: str,
    analysis_type: str,
    syllabus_name: str,
    jd_role: str,
    cosine_similarity: float,
    gap_index_score: float,
    missing_skills_json: str,
    matching_skills_json: str,
) -> None:
    user_id = _get_user_id(username)
    if user_id is None:
        return  # User not found — silent no-op (mirrors old behaviour)
    sb = get_supabase()
    sb.table("reports").insert(
        {
            "user_id": user_id,
            "analysis_type": analysis_type,
            "syllabus_name": syllabus_name,
            "jd_role": jd_role,
            "cosine_similarity": cosine_similarity,
            "gap_index_score": gap_index_score,
            "missing_skills_json": missing_skills_json,
            "matching_skills_json": matching_skills_json,
        }
    ).execute()


def get_reports_for_user(username: str) -> list[Report]:
    user_id = _get_user_id(username)
    if user_id is None:
        return []
    sb = get_supabase()
    res = (
        sb.table("reports")
        .select("*")
        .eq("user_id", user_id)
        .order("timestamp", desc=True)
        .execute()
    )
    return [_row_to_report(row) for row in (res.data or [])]


def clear_reports_for_user(username: str) -> None:
    user_id = _get_user_id(username)
    if user_id is None:
        return
    sb = get_supabase()
    sb.table("reports").delete().eq("user_id", user_id).execute()


# ---------------------------------------------------------------------------
# Authenticator credential builder  (used by auth.py)
# ---------------------------------------------------------------------------

def credentials_dict_for_authenticator() -> dict:
    """
    Shape expected by streamlit-authenticator:
        {'usernames': {uname: {email, name, password}}}
    """
    sb = get_supabase()
    res = (
        sb.table("users")
        .select("username, email, display_name, password_hash")
        .execute()
    )
    users = res.data or []
    return {
        "usernames": {
            u["username"]: {
                "email": u["email"],
                "name": u["display_name"],
                "password": u["password_hash"],
            }
            for u in users
        }
    }
