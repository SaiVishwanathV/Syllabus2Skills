# From Syllabus to Skills: An NLP-Driven Framework for Curriculum–Industry Skill Gap Analysis

## Summary

Educational curricula often lag behind rapidly evolving industry requirements, leading to a mismatch between the skills students acquire and those demanded by employers. This project presents *Syllabus2Skills*, an end-to-end natural language processing (NLP) framework that automatically analyzes academic syllabus documents and compares them with real-world job descriptions to identify skill gaps.

The system extracts relevant skills from syllabus content and industry job postings, computes similarity scores, and highlights missing or weak competencies. It provides an interactive interface for users to upload syllabus documents, select target job roles, and visualize skill alignment through intuitive dashboards.

---

## Statement of Need

Bridging the gap between academic learning and industry expectations is a critical challenge in modern education. Students often graduate with theoretical knowledge but lack practical skills aligned with current job market demands. Existing approaches to curriculum evaluation are largely manual, time-consuming, and subjective.

There is a need for an automated, scalable, and data-driven system that:

* Quantifies the alignment between curriculum content and industry requirements
* Identifies missing or weak skills
* Provides actionable insights for students and educators

*Syllabus2Skills* addresses this need by leveraging NLP techniques to systematically evaluate and compare curriculum content with job market data.

---

## Related Work

Previous studies have explored skill extraction and job–curriculum alignment using traditional text mining and keyword matching techniques. Methods such as TF-IDF and cosine similarity have been widely used for document comparison tasks.

More recent approaches incorporate advanced embeddings (e.g., BERT) for semantic understanding. However, many existing systems lack:

* End-to-end integration
* User-friendly interfaces
* Real-time analysis capabilities

This project contributes by combining established NLP techniques with an interactive system design, making skill gap analysis accessible and practical.

---

## System Architecture

The system follows a modular architecture consisting of:

* **Frontend**: Built using Streamlit for interactive user experience
* **Backend**: FastAPI-based services for processing and analysis
* **NLP Pipeline**:

  * Text extraction from PDFs
  * Tokenization and preprocessing
  * TF-IDF vectorization
  * Cosine similarity computation
* **Database**: Supabase for storing user and analysis data

---

## Functionality

The system provides the following features:

* Upload syllabus documents (PDF format)
* Select target job roles from industry datasets
* Extract and analyze skills using NLP techniques
* Compute skill similarity and gap scores
* Visualize results through graphs and dashboards
* Compare resume content with job descriptions

---

## Implementation

The core implementation uses:

* **Python** as the primary programming language
* **NLTK** for text preprocessing
* **Scikit-learn** for TF-IDF vectorization and similarity computation
* **Streamlit** for frontend visualization
* **FastAPI** for backend APIs
* **Supabase** for database integration

---

## Results and Impact

The system successfully identifies discrepancies between academic curricula and industry requirements. It provides:

* Quantitative skill gap metrics
* Visual representation of skill coverage
* Actionable insights for skill improvement

This can be used by:

* Students to improve employability
* Educators to update curriculum
* Institutions for data-driven academic planning

---

## Conclusion

*Syllabus2Skills* demonstrates how NLP techniques can be effectively applied to bridge the gap between education and industry. The system offers a scalable and practical solution for automated skill gap analysis, contributing to improved alignment between academic programs and job market demands.

---

## References

* Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval.
* Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information Retrieval.
* Devlin, J., et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
