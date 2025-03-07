import sys
import re
import pdfplumber
import os

# Predefined list of technical keywords (expand as needed)
TECHNICAL_KEYWORDS = {
    "programming_languages": [
        "Python", "Java", "C++", "C#", "JavaScript", "Ruby", "Go", "Rust", "PHP", "Swift", "Kotlin", "TypeScript",
        "SQL", "R", "Perl", "Scala", "Haskell", "Lua"
    ],
    "frameworks_tools": [
        "Django", "Flask", "Spring", "React", "Angular", "Vue.js", "Node.js", "Express", "TensorFlow", "PyTorch",
        "Git", "Docker", "Kubernetes", "Jenkins", "AWS", "Azure", "GCP", "Terraform", "Ansible", "Maven", "Gradle"
    ],
    "concepts_approaches": [
        "Agile", "Scrum", "DevOps", "CI/CD", "OOP", "Functional Programming", "REST", "GraphQL", "Microservices",
        "TDD", "BDD", "Design Patterns", "SOLID", "DRY", "Machine Learning", "Deep Learning", "Big Data", "Cloud Computing"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Redis", "Cassandra", "DynamoDB"
    ]
}

# Combine all keywords into a single set for efficient lookup
ALL_KEYWORDS = set(
    sum(TECHNICAL_KEYWORDS.values(), [])
)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def extract_keywords(text):
    """Extract technical keywords from text without section assumptions."""
    found_keywords = set()
    text_lower = text.lower()

    # Use regex with word boundaries to match whole words
    for keyword in ALL_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower):
            found_keywords.add(keyword)

    return found_keywords

def categorize_keywords(keywords):
    """Categorize found keywords into predefined groups."""
    categorized = {
        "programming_languages": [],
        "frameworks_tools": [],
        "concepts_approaches": [],
        "databases": []
    }
    for keyword in keywords:
        for category, keyword_list in TECHNICAL_KEYWORDS.items():
            if keyword in keyword_list:
                categorized[category].append(keyword)
                break
    return categorized

def parse_cv(cv_path):
    """Parse a CV from the given file location and extract technical keywords."""
    if not cv_path.endswith('.pdf'):
        print("Error: Only PDF files are supported.")
        return

    if not os.path.exists(cv_path):
        print(f"Error: File not found at {cv_path}")
        return

    print(f"\nParsing CV at: {cv_path}")

    # Extract text from the CV
    cv_text = extract_text_from_pdf(cv_path)
    if not cv_text:
        print("No text could be extracted from the CV.")
        return

    # Extract and categorize keywords
    keywords = extract_keywords(cv_text)
    if not keywords:
        print("No technical keywords found in the CV.")
        return

    categorized_keywords = categorize_keywords(keywords)
    print("\nExtracted Technical Keywords:")
    for category, kw_list in categorized_keywords.items():
        if kw_list:
            print(f"  {category.replace('_', ' ').title()}: {', '.join(kw_list)}")

if __name__ == "__main__":
    cv_path = "Ranjan_Lamsal_cv.pdf"
    parse_cv(cv_path)