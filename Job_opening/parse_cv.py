# Job_opening/tasks.py
import re
import pdfplumber
from celery import shared_task
from .models import ApplicantResponse  # Import the model

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

ALL_KEYWORDS = set(sum(TECHNICAL_KEYWORDS.values(), []))

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
    """Extract technical keywords from text."""
    found_keywords = set()
    text_lower = text.lower()
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

@shared_task
def parse_cv_keywords(applicant_response_id):
    """Parse the CV and save keywords to the ApplicantResponse model."""
    try:
        # Retrieve the ApplicantResponse instance
        response = ApplicantResponse.objects.get(id=applicant_response_id)
        cv_path = response.cv.path

        # Extract text from the CV
        cv_text = extract_text_from_pdf(cv_path)
        if not cv_text:
            print(f"No text extracted from CV at {cv_path}")
            return None

        # Extract and categorize keywords
        keywords = extract_keywords(cv_text)
        if not keywords:
            print(f"No technical keywords found in CV at {cv_path}")
            response.cv_keywords = {}  # Save empty dict if no keywords
            response.save(update_fields=['cv_keywords'])
            return None

        categorized_keywords = categorize_keywords(keywords)
        print(f"\nKeywords extracted from CV at {cv_path}:")
        for category, kw_list in categorized_keywords.items():
            if kw_list:
                print(f"  {category.replace('_', ' ').title()}: {', '.join(kw_list)}")

        # Save the categorized keywords to the model
        response.cv_keywords = categorized_keywords
        response.save(update_fields=['cv_keywords'])

        return categorized_keywords  # Optional: return for debugging
    except ApplicantResponse.DoesNotExist:
        print(f"Error: ApplicantResponse with ID {applicant_response_id} not found")
        return None
    except Exception as e:
        print(f"Error processing CV for applicant {applicant_response_id}: {str(e)}")
        return None