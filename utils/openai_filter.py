import streamlit as st
from openai import OpenAI
import json
from typing import List


_GENERIC_TERMS = {
    "none",
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
    "rest",
    "boot",
}

_TECH_ANCHORS = {
    "java",
    "python",
    "sql",
    "mysql",
    "postgresql",
    "oracle",
    "mongodb",
    "redis",
    "spring",
    "microservice",
    "docker",
    "kubernetes",
    "git",
    "github",
    "jenkins",
    "cicd",
    "junit",
    "testing",
    "aws",
    "azure",
    "gcp",
    "kafka",
    "rabbitmq",
}


def _local_filter(raw_keywords: List[str]) -> List[str]:
    cleaned: List[str] = []
    for kw in raw_keywords:
        if not isinstance(kw, str):
            continue
        s = kw.strip().lower()
        if not s or s in _GENERIC_TERMS:
            continue
        if any(anchor in s for anchor in _TECH_ANCHORS):
            cleaned.append(s)
    return list(dict.fromkeys(cleaned))


@st.cache_data(show_spinner=False)
def filter_technical_skills(raw_keywords: List[str]) -> List[str]:
    """
    Uses OpenAI to filter out non-technical terms from a list of keywords.
    Ensures 100% precision by removing soft skills and generic buzzwords.
    """
    local_first = _local_filter(raw_keywords)
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        return local_first or raw_keywords

    try:
        client = OpenAI(api_key=api_key)
        
        # We only send a subset to keep it fast and cheap
        # Top 150 is usually more than enough for a JD match
        input_list = raw_keywords[:150]
        
        prompt = f"""
        You are a strict technical recruiter. 
        Below is a list of potential technical skills and keywords extracted from a job description.
        Filter this list and return ONLY the hard technical skills, tools, programming languages, frameworks, and specific technical domains.
        
        STRICTLY REMOVE:
        - Soft skills (communication, leadership, teamwork, etc.)
        - Generic business terms (solution, environment, process, management, etc.)
        - Verbs and adjectives (designing, working, strong, etc.)
        - Non-technical nouns (business, engineer, system, tool, etc.)
        
        Return the result as a raw JSON array of strings. Do not include any explanation or markdown.
        
        Input list:
        {json.dumps(input_list)}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional technical skill extractor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={ "type": "json_object" },
            timeout=8,
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        
        # The AI might return {"skills": [...]} or just the array depending on how it interprets JSON object mode
        if isinstance(data, dict):
            # Look for an array inside the dict
            for key in data:
                if isinstance(data[key], list):
                    ai_list = [str(x).strip().lower() for x in data[key] if isinstance(x, str)]
                    return _local_filter(ai_list) or local_first or raw_keywords
        
        if isinstance(data, list):
            ai_list = [str(x).strip().lower() for x in data if isinstance(x, str)]
            return _local_filter(ai_list) or local_first or raw_keywords
            
        return local_first or raw_keywords

    except Exception:
        return local_first or raw_keywords
