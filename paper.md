---
title: "From Syllabus to Skills: An NLP-Driven Framework for Curriculum–Industry Skill Gap Analysis"

tags:
- Python
- Natural Language Processing
- Machine Learning
- Skill Gap Analysis

authors:
- name: Sai Vishwanath Vummintala
  affiliation: 1
- name: Udbhav Tummala
  affiliation: 1
- name: Dr. A. Ratna Raju
  affiliation: 1
- name: Dr. K. Mahesh Kumar
  affiliation: 1

affiliations:
- name: Mahatma Gandhi Institute of Technology, Hyderabad, India
  index: 1

date: 2026
---

# Summary

The rapid evolution of industry requirements has created a significant gap between academic curricula and real-world job expectations. This paper presents *From Syllabus to Skills*, an NLP-driven software system that automatically analyzes and quantifies the curriculum–industry skill gap.

The framework processes academic syllabus documents and compares extracted skills with industry job requirements using TF-IDF vectorization @salton1988 and cosine similarity techniques. It generates a quantitative skill gap score along with matched and missing skills.

The system is implemented as a full-stack application using Streamlit for the frontend, FastAPI for the backend, and Supabase (PostgreSQL) for data storage. It provides an interactive interface for analyzing curriculum effectiveness and identifying skill deficiencies.

The source code is openly available at:  
https://github.com/SaiVishwanathV/Syllabus2Skills

---

# Statement of Need

Academic curricula often fail to keep pace with rapidly evolving industry demands, resulting in graduates lacking essential practical skills. Traditional curriculum evaluation methods are manual, subjective, and not scalable.

There is a clear need for an automated system that can:
- Extract skills from academic syllabi  
- Compare them with real-world job requirements  
- Quantify the skill gap in a measurable way  

This software addresses that need by providing a data-driven NLP-based framework, building upon prior research on curriculum–industry gaps @ahadi2022skills that bridges academia and industry. It enables students, educators, and institutions to identify missing competencies and improve employability outcomes.

---

# Software Description

## Architecture

The system follows a modular full-stack architecture:

- **Frontend**: Streamlit (interactive UI and visualization)  
- **Backend**: FastAPI (API handling and processing)  
- **Database**: Supabase (PostgreSQL)  

## NLP Pipeline

- TF-IDF Vectorization @salton1988
- Cosine Similarity  

## Workflow

1. User uploads a syllabus PDF  
2. Text is extracted from the document  
3. Skills are identified using NLP techniques  
4. Job role skills are retrieved from dataset  
5. Similarity comparison is performed  
6. Output generated:
   - Matched skills  
   - Missing skills  
   - Skill gap score  

---

# Features

- Automated skill extraction from syllabus PDFs  
- Industry skill extraction from job datasets  
- TF-IDF based text vectorization  
- Cosine similarity for skill matching  
- Quantitative skill gap scoring  
- Identification of missing and matched skills  
- Interactive visualization using Streamlit  
- Scalable full-stack architecture  

---

# Example Usage

A user uploads a syllabus document and selects the role *Software Engineer*.

The system:
- Extracts skills such as Python, DBMS, and Operating Systems  
- Compares them with industry requirements  
- Outputs:
  - Matched skills: Python, SQL  
  - Missing skills: Docker, AWS, Microservices  
  - Skill gap score: 0.45  

This enables users to clearly understand curriculum deficiencies and align learning outcomes with industry expectations.

---

# Evaluation

The system was tested on multiple syllabus documents and job roles.

The results demonstrate that:
- Relevant skills can be effectively extracted from unstructured syllabus text  
- Missing skills identified align with real-world industry expectations  
- The computed skill gap score provides a meaningful quantitative indicator  

Future enhancements can include transformer-based embeddings to improve semantic understanding and accuracy.

---

# Software Availability

The source code is available at:

https://github.com/SaiVishwanathV/Syllabus2Skills

## Requirements

The software requires Python 3.8 or higher.

## Installation

Clone the repository:

```bash
git clone https://github.com/SaiVishwanathV/Syllabus2Skills.git
cd Syllabus2Skills
