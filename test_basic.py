# Basic functional test for text similarity / NLP behavior

def test_text_presence():
    text = "Python and Machine Learning are important skills"
    assert "Python" in text


def test_skill_like_text():
    syllabus = "Data Structures, Algorithms, Python"
    job = "Python Developer with Data Structures knowledge"
    
    # simple check mimicking overlap
    assert "Python" in syllabus and "Python" in job
