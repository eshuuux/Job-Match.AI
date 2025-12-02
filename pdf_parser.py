import PyPDF2

# Pre-defined skill list
SKILLS = [
    "python", "java", "c", "c++", "html", "css", "javascript", "bootstrap",
    "flask", "django", "rest api", "react", "nodejs",
    "sql", "sqlite", "mysql", "mongodb",
    "git", "github", "linux"
]

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as pdf:
        reader = PyPDF2.PdfReader(pdf)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text.lower()

def find_skills(text):
    found_skills = []
    for skill in SKILLS:
        if skill.lower() in text:
            found_skills.append(skill)
    return found_skills

def parse_resume(file_path):
    text = extract_text_from_pdf(file_path)
    return find_skills(text)
