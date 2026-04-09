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
- name: Mahatma Gandhi Institute of Technology, Gandipet, Hyderabad-500075, India
  index: 1

date: 2026

# Summary

The rapid evolution of industry requirements has led to a persistent gap between academic curricula and real-world job market expectations. This paper presents From Syllabus to Skills, an NLP-driven software framework designed to automatically analyze and quantify the curriculum–industry skill gap.

The framework accepts academic syllabi in PDF format along with a selected target job role and processes them through an end-to-end pipeline for skill extraction and comparison. Statistical natural language processing techniques such as TF-IDF and cosine similarity are used to identify relevant skills from unstructured syllabus text.

The framework computes a quantitative skill gap score, identifies missing and matched skills, and provides structured analytical outputs. An interactive web-based interface built using Streamlit presents these results through intuitive visualizations, enabling users to clearly interpret strengths and deficiencies in the curriculum.

The novelty of this work lies in integrating academic syllabus analysis with real-world job datasets in a unified, automated system for quantifiable skill gap assessment. The system can assist institutions in curriculum redesign and improve student employability outcomes.

The proposed system is implemented as a scalable full-stack application using a Streamlit-based frontend, FastAPI backend, and PostgreSQL (Supabase) database, ensuring modularity, performance, and ease of deployment. The job role data is derived from curated real-world job postings, enabling meaningful comparison with industry expectations.

# Statement of Need

The disconnect between academic curricula and rapidly evolving industry requirements has become a critical challenge in higher education. Traditional curriculum design processes are often slow to adapt, resulting in graduates lacking key practical skills demanded by employers. This misalignment contributes to reduced employability and necessitates additional training efforts after graduation.

Existing approaches to curriculum evaluation are largely manual, subjective, and limited in scalability. While some tools analyze job market trends or educational content independently, there is a lack of integrated, automated systems that directly compare academic syllabi with industry skill requirements in a quantifiable manner.

From Syllabus to Skills addresses this gap by providing a software-driven, data-centric framework that bridges academia and industry expectations. By leveraging natural language processing techniques, the system transforms unstructured syllabus documents into structured skill representations and systematically compares them with industry requirements.

This software enables stakeholders including students, educators, and academic institutions to identify missing competencies, measure curriculum effectiveness, and make informed data-driven decisions. Compared to conventional approaches, the framework offers an automated, scalable, and reproducible solution for continuous curriculum evaluation and improvement.

# Features

The software provides the following core capabilities:

- Automated extraction of skills from academic syllabus PDFs
- Industry skill extraction from curated job datasets
- TF-IDF based text vectorization
- Cosine similarity for skill matching
- Quantitative skill gap scoring
- Identification of missing and matched skills
- Interactive visualization using Streamlit
- Full-stack architecture with FastAPI and Supabase

# Implementation

The system follows a modular architecture consisting of:

- Frontend: Streamlit for visualization and user interaction
- Backend: FastAPI for request handling and processing
- Database: Supabase (PostgreSQL) for structured data storage
- NLP Pipeline: TF-IDF vectorization and cosine similarity

The workflow involves extracting text from syllabus documents, identifying relevant skills, comparing them with industry job requirements, and generating interpretable analytical outputs.

# Acknowledgements

The authors would like to thank their mentors and faculty members for their guidance and support throughout this work. We also acknowledge the support provided by Mahatma Gandhi Institute of Technology, Hyderabad.

Additionally, we thank the open-source community and contributors of tools such as Streamlit, FastAPI, Scikit-learn, and NLTK.

# References

- Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press.
- Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management*, 24(5), 513–523.