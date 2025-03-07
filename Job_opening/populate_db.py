import requests
import random
from datetime import datetime
from io import BytesIO
import json


BASE_URL = "http://127.0.0.1:8000"
SIGNUP_URL = f"{BASE_URL}/auth/signup/"
LOGIN_URL = f"{BASE_URL}/auth/login/"
JOB_URL = f"{BASE_URL}/openings/job-openings/"
APPLY_URL = f"{BASE_URL}/openings/apply/"

# Dummy Data

# Companies (5)
companies = [
    {"name": "TechTrend Innovations", "email": "contact@techtrend.com", "username": "techtrend", "password": "Tech123!"},
    {"name": "GreenLeaf Solutions", "email": "info@greenleaf.com", "username": "greenleaf", "password": "Green456@"},
    {"name": "BlueSky Enterprises", "email": "support@bluesky.com", "username": "bluesky", "password": "Blue789#"},
    {"name": "RedRock Technologies", "email": "hr@redrock.com", "username": "redrock", "password": "Red101$"},
    {"name": "SilverLining Systems", "email": "admin@silverlining.com", "username": "silverlining", "password": "Silver202&"}
]

# Job Openings (25 total, 5 per company)
job_templates = [
    {
        "title": "Software Engineer",
        "description": "Develop innovative software solutions.",
        "deadline": "2025-04-01T23:59:59Z",
        "form_variations": [
            [{"question": "Years coding", "field_type": "number", "is_required": True}, {"question": "Languages", "field_type": "choice", "is_required": True, "options": ["Python", "Java", "C++"]}],
            [{"question": "Coding experience", "field_type": "number", "is_required": True}, {"question": "Frameworks", "field_type": "text", "is_required": False}],
            [{"question": "Dev years", "field_type": "number", "is_required": True}, {"question": "Open source contrib?", "field_type": "choice", "is_required": True, "options": ["Yes", "No"]}],
            [{"question": "Experience in years", "field_type": "number", "is_required": True}, {"question": "Preferred IDE", "field_type": "text", "is_required": False}],
            [{"question": "Software exp", "field_type": "number", "is_required": True}, {"question": "Team size", "field_type": "number", "is_required": False}]
        ]
    },
    {
        "title": "Data Analyst",
        "description": "Analyze data for insights.",
        "deadline": "2025-03-20T23:59:59Z",
        "form_variations": [
            [{"question": "Stats tools", "field_type": "text", "is_required": True}, {"question": "SQL exp", "field_type": "choice", "is_required": True, "options": ["Yes", "No"]}],
            [{"question": "Data tools", "field_type": "text", "is_required": True}, {"question": "Years analyzing", "field_type": "number", "is_required": False}],
            [{"question": "Analytics software", "field_type": "text", "is_required": True}, {"question": "Visualization exp", "field_type": "choice", "is_required": True, "options": ["Tableau", "Power BI", "None"]}],
            [{"question": "Tool proficiency", "field_type": "text", "is_required": True}, {"question": "Data volume handled", "field_type": "number", "is_required": False}],
            [{"question": "Analysis tools", "field_type": "text", "is_required": True}, {"question": "Certifications", "field_type": "text", "is_required": False}]
        ]
    },
    {
        "title": "QA Engineer",
        "description": "Ensure product quality.",
        "deadline": "2025-03-15T23:59:59Z",
        "form_variations": [
            [{"question": "Testing tools", "field_type": "text", "is_required": True}, {"question": "Automation yrs", "field_type": "number", "is_required": False}],
            [{"question": "QA frameworks", "field_type": "text", "is_required": True}, {"question": "Bug tracking", "field_type": "choice", "is_required": True, "options": ["JIRA", "Bugzilla", "Other"]}],
            [{"question": "Test platforms", "field_type": "text", "is_required": True}, {"question": "Manual exp", "field_type": "number", "is_required": False}],
            [{"question": "Quality tools", "field_type": "text", "is_required": True}, {"question": "Test automation", "field_type": "choice", "is_required": True, "options": ["Yes", "No"]}],
            [{"question": "QA experience", "field_type": "text", "is_required": True}, {"question": "Test cases written", "field_type": "number", "is_required": False}]
        ]
    },
    {
        "title": "Product Manager",
        "description": "Lead product strategy.",
        "deadline": "2025-04-10T23:59:59Z",
        "form_variations": [
            [{"question": "PM years", "field_type": "number", "is_required": True}, {"question": "Methodology", "field_type": "choice", "is_required": True, "options": ["Scrum", "Kanban"]}],
            [{"question": "Product exp", "field_type": "number", "is_required": True}, {"question": "Team size managed", "field_type": "number", "is_required": False}],
            [{"question": "Years in PM", "field_type": "number", "is_required": True}, {"question": "Roadmap tools", "field_type": "text", "is_required": False}],
            [{"question": "Management exp", "field_type": "number", "is_required": True}, {"question": "Stakeholder exp", "field_type": "choice", "is_required": True, "options": ["Yes", "No"]}],
            [{"question": "PM tenure", "field_type": "number", "is_required": True}, {"question": "Product launches", "field_type": "number", "is_required": False}]
        ]
    },
    {
        "title": "DevOps Engineer",
        "description": "Manage infrastructure.",
        "deadline": "2025-03-25T23:59:59Z",
        "form_variations": [
            [{"question": "Cloud platforms", "field_type": "text", "is_required": True}, {"question": "CI/CD tools", "field_type": "choice", "is_required": False, "options": ["Jenkins", "GitLab CI"]}],
            [{"question": "Infra tools", "field_type": "text", "is_required": True}, {"question": "Years in DevOps", "field_type": "number", "is_required": False}],
            [{"question": "Cloud exp", "field_type": "text", "is_required": True}, {"question": "Container exp", "field_type": "choice", "is_required": True, "options": ["Docker", "Kubernetes", "None"]}],
            [{"question": "DevOps tools", "field_type": "text", "is_required": True}, {"question": "Monitoring exp", "field_type": "number", "is_required": False}],
            [{"question": "Infrastructure", "field_type": "text", "is_required": True}, {"question": "Automation tools", "field_type": "text", "is_required": False}]
        ]
    }
]

# Applicants (20 unique users)
applicants = [
    {"email": "alice.johnson@example.com", "name": "Alice Johnson", "gender": "female", "country": "USA", "phone": "+12025550123"},
    {"email": "bob.smith@example.com", "name": "Bob Smith", "gender": "male", "country": "Canada", "phone": "+14165550123"},
    {"email": "clara.lee@example.com", "name": "Clara Lee", "gender": "female", "country": "UK", "phone": "+447700900123"},
    {"email": "david.kim@example.com", "name": "David Kim", "gender": "male", "country": "South Korea", "phone": "+821012345678"},
    {"email": "emma.wong@example.com", "name": "Emma Wong", "gender": "female", "country": "Australia", "phone": "+61412345678"},
    {"email": "frank.brown@example.com", "name": "Frank Brown", "gender": "male", "country": "Germany", "phone": "+4917612345678"},
    {"email": "grace.chen@example.com", "name": "Grace Chen", "gender": "female", "country": "China", "phone": "+8613912345678"},
    {"email": "henry.davis@example.com", "name": "Henry Davis", "gender": "male", "country": "USA", "phone": "+12035550123"},
    {"email": "isabella.martin@example.com", "name": "Isabella Martin", "gender": "female", "country": "France", "phone": "+33612345678"},
    {"email": "james.park@example.com", "name": "James Park", "gender": "male", "country": "Japan", "phone": "+81312345678"},
    {"email": "kate.evans@example.com", "name": "Kate Evans", "gender": "female", "country": "UK", "phone": "+447800900123"},
    {"email": "liam.nguyen@example.com", "name": "Liam Nguyen", "gender": "male", "country": "Vietnam", "phone": "+84901234567"},
    {"email": "mia.garcia@example.com", "name": "Mia Garcia", "gender": "female", "country": "Spain", "phone": "+34612345678"},
    {"email": "noah.ali@example.com", "name": "Noah Ali", "gender": "male", "country": "India", "phone": "+919876543210"},
    {"email": "olivia.silva@example.com", "name": "Olivia Silva", "gender": "female", "country": "Brazil", "phone": "+5511987654321"},
    {"email": "peter.jones@example.com", "name": "Peter Jones", "gender": "male", "country": "USA", "phone": "+12045550123"},
    {"email": "quinn.taylor@example.com", "name": "Quinn Taylor", "gender": "female", "country": "Canada", "phone": "+14175550123"},
    {"email": "raj.patel@example.com", "name": "Raj Patel", "gender": "male", "country": "India", "phone": "+919012345678"},
    {"email": "sophia.hernandez@example.com", "name": "Sophia Hernandez", "gender": "female", "country": "Mexico", "phone": "+5215512345678"},
    {"email": "thomas.white@example.com", "name": "Thomas White", "gender": "male", "country": "Australia", "phone": "+61422345678"}
]


def populate_database():
    company_tokens = []

    # Step 1: Register 5 companies
    print("Registering companies...")
    for company in companies:
        response = requests.post(SIGNUP_URL, json=company)
        if response.status_code == 201:
            print(f"Registered {company['name']} successfully.")
        else:
            print(f"Failed to register {company['name']}: {response.text}")
            return

    # Step 2: Login to each company
    print("\nLogging in companies...")
    for company in companies:
        login_data = {"username": company["username"], "password": company["password"]}
        response = requests.post(LOGIN_URL, json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            company_tokens.append({"company": company["name"], "access": tokens["access"], "refresh": tokens["refresh"]})
            print(f"Logged in {company['name']} successfully.")
        else:
            print(f"Failed to login {company['name']}: {response.text}")
            return

    # Step 3: Create 5 jobs per company (25 total)
    print("\nCreating jobs...")
    job_ids = {}
    for token in company_tokens:
        headers = {"Authorization": f"Bearer {token['access']}", "Content-Type": "application/json"}
        job_ids[token["company"]] = []
        for i, job_template in enumerate(job_templates):
            job = {
                "title": job_template["title"],
                "description": job_template["description"],
                "deadline": job_template["deadline"],
                "form_fields": job_template["form_variations"][i]
            }
            response = requests.post(JOB_URL, headers=headers, json=job)
            if response.status_code == 201:
                job_id = response.json()["id"]
                job_ids[token["company"]].append(job_id)
                print(f"Created '{job['title']}' for {token['company']} (ID: {job_id}).")
            else:
                print(f"Failed to create job for {token['company']}: {response.text}")
                return

    # Step 4: Populate applicant responses with CVs
    print("\nPopulating applicant responses...")
    all_job_ids = [job_id for company_jobs in job_ids.values() for job_id in company_jobs]
    for applicant in applicants:
        num_applications = random.randint(3, 5)
        selected_jobs = random.sample(all_job_ids, num_applications)
        
        for job_id in selected_jobs:
            company = next(c for c, ids in job_ids.items() if job_id in ids)
            headers = {"Authorization": f"Bearer {next(t['access'] for t in company_tokens if t['company'] == company)}"}
            job_response = requests.get(f"{JOB_URL}{job_id}/", headers=headers).json()
            job_template = next(j for j in job_templates if j["title"] == job_response["title"])
            form_fields = job_template["form_variations"][job_templates.index(job_template)]

            if datetime.strptime(job_response["deadline"], "%Y-%m-%dT%H:%M:%SZ") <= datetime.utcnow():
                print(f"Skipping response for {applicant['name']} to expired job ID {job_id} ({job_response['title']}).")
                continue

            responses = {}
            for field in form_fields:
                if field["field_type"] == "number":
                    responses[field["question"]] = str(random.randint(1, 10))
                elif field["field_type"] == "text":
                    responses[field["question"]] = f"Skill{random.randint(1, 5)}"
                elif field["field_type"] == "choice":
                    responses[field["question"]] = random.choice(field["options"])

            # Create a dummy PDF CV
            cv_content = BytesIO(f"Dummy CV for {applicant['name']}".encode("utf-8"))
            cv_file = {"cv": ("cv.pdf", cv_content, "application/pdf")}

            data = {
                "email_address": applicant["email"],
                "name": applicant["name"],
                "gender": applicant["gender"],
                "country": applicant["country"],
                "phone_number": applicant["phone"],
                "responses": json.dumps(responses)  # Send as JSON string
            }

            response = requests.post(f"{APPLY_URL}{job_id}/", files=cv_file, data=data)
            if response.status_code == 201:
                print(f"Added response with CV for {applicant['name']} to job ID {job_id} ({job_response['title']}).")
            else:
                print(f"Failed to add response for {applicant['name']} to job ID {job_id}: {response.text}")

if __name__ == "__main__":
    populate_database()