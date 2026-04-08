# From Syllabus to Skills: NLP-Driven Skill Gap Analysis Framework

## 📌 Overview

*From Syllabus to Skills* is an NLP-driven software system that analyzes academic syllabus documents and compares them with real-world industry job requirements to identify skill gaps.

The system extracts skills from syllabus PDFs using natural language processing techniques and matches them against dynamically sourced industry skills to compute a skill gap score and highlight missing competencies.

---

## 🚀 Features

* Automated syllabus parsing from PDF documents
* NLP-based skill extraction using TF-IDF and NLTK
* Skill matching using similarity techniques
* Quantitative skill gap scoring
* Identification of missing industry-relevant skills
* Interactive visualization of results
* Integration with real-world job role data

---

## 🧠 Technology Stack

* **Frontend / UI**: Streamlit
* **Backend API**: FastAPI
* **Database**: Supabase (PostgreSQL)
* **NLP & ML**: NLTK, Scikit-learn
* **AI Integration**: OpenAI API
* **Visualization**: Plotly

---

## ⚙️ Installation

```bash
git clone https://github.com/SaiVishwanathV/Syllabus2Skills.git
cd Syllabus2Skills
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the application:

```bash
streamlit run app.py
```

Upload a syllabus PDF, select a target job role, and view the generated skill gap analysis.

---

## 📊 Methodology

1. **Data Ingestion**

   * Upload syllabus PDF
   * Extract raw text using PDF parsing

2. **Preprocessing**

   * Tokenization
   * Stopword removal
   * Text normalization

3. **Skill Extraction**

   * TF-IDF vectorization
   * Keyword extraction

4. **Skill Matching**

   * Cosine similarity between syllabus skills and job skills

5. **Gap Analysis**

   * Identify missing and weak skills
   * Compute skill gap score

---

## 📄 Research Contribution

This project proposes a scalable NLP-based framework to bridge the gap between academic curriculum and industry expectations by:

* Automating curriculum analysis
* Providing measurable skill gap insights
* Enabling data-driven curriculum improvements

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙌 Acknowledgements

* Open-source NLP libraries (NLTK, Scikit-learn)
* FastAPI and Streamlit communities
* Supabase for backend infrastructure

---

