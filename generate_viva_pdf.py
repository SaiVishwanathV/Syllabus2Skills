
from fpdf import FPDF
import re


def clean_txt(text):
    if not text: return ""
    # Remove all non-printable ASCII characters
    cleaned = "".join(i for i in text if 31 < ord(i) < 127 or i == "\n")
    return cleaned.strip()

class VivaPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "I", 8)
            self.set_x(10)
            self.cell(0, 10, "Syllabus to Skills - Viva Preparation Guide", border=0, align="R", ln=1)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, label):
        label = clean_txt(label)
        if not label: label = "Section"
        self.add_page()
        self.set_font("helvetica", "B", 16)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 12, label, ln=1, fill=True)
        self.ln(4)

    def add_question(self, q, a):
        q = clean_txt(q)
        if not q: return
        
        # Ensure we are at the left margin
        self.set_x(10)
        
        # Question
        self.set_font("helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, f"Q: {q}")
        
        # Answer
        self.set_x(10)
        self.set_font("helvetica", "", 11)
        self.set_text_color(0, 0, 0)
        
        parts = a.split("👉")
        main_a = clean_txt(parts[0])
        if main_a:
            self.multi_cell(0, 6, main_a)
        
        if len(parts) > 1:
            sub_a = clean_txt(parts[1])
            if sub_a:
                self.set_x(15) # Indent logic
                self.set_font("helvetica", "I", 10)
                self.set_text_color(100, 100, 100)
                self.multi_cell(0, 6, f"[Logic]: {sub_a}")
        
        self.set_text_color(0, 0, 0)
        self.ln(4)

def generate_pdf():
    pdf = VivaPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()

    # --- Title Page ---
    pdf.add_page()
    pdf.ln(60)
    pdf.set_font("helvetica", "B", 24)
    pdf.cell(0, 20, "SYLLABUS TO SKILLS", ln=1, align="C")
    pdf.set_font("helvetica", "", 18)
    pdf.cell(0, 10, "NLP-Based Skill Gap Analysis", ln=1, align="C")
    pdf.ln(20)
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "VIVA PREPARATION GUIDE", ln=1, align="C")
    pdf.ln(60)
    pdf.set_font("helvetica", "I", 12)
    pdf.cell(0, 10, "Resource for Computer Science Students", ln=1, align="C")

    # --- Content ---
    try:
        with open("viva_prep_guide.md", "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Split by sections (##)
    sections = re.split(r'\n## ', content)
    
    for section in sections:
        section = section.strip()
        if not section or "TABLE OF CONTENTS" in section:
            continue
            
        pdf.add_page()
        lines = section.split("\n")
        title = lines[0].replace("#", "").strip()
        pdf.chapter_title(title)
        
        current_q = None
        current_a = ""
        
        for line in lines[1:]:
            line = line.strip()
            if not line: continue
            
            if line.startswith("**Q:"):
                if current_q:
                    pdf.add_question(current_q, current_a)
                current_q = line.replace("**Q:", "").replace("**", "").strip()
                current_a = ""
            elif line.startswith("**A:"):
                current_a = line.replace("**A:", "").replace("**", "").strip()
            elif line.startswith("👉") or line.startswith("* "):
                current_a += " " + line
            elif line.startswith("###"):
                if current_q:
                    pdf.add_question(current_q, current_a)
                    current_q = None
                sub_title = line.replace("###", "").strip()
                pdf.set_font("helvetica", "B", 13)
                pdf.cell(0, 10, clean_txt(sub_title), ln=1)
                pdf.ln(2)
            else:
                if current_q:
                    current_a += " " + line
                else:
                    pdf.set_font("helvetica", "", 10)
                    pdf.multi_cell(0, 5, clean_txt(line))
        
        if current_q:
            pdf.add_question(current_q, current_a)

    output_file = "Viva_Prep_Syllabus_to_Skills.pdf"
    pdf.output(output_file)
    print(f"Successfully generated {output_file}")

if __name__ == "__main__":
    generate_pdf()
