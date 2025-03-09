import requests
import random
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database_population.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"
SIGNUP_URL = f"{BASE_URL}/auth/signup/"
LOGIN_URL = f"{BASE_URL}/auth/login/"
JOB_URL = f"{BASE_URL}/openings/job-openings/"
APPLY_URL = f"{BASE_URL}/openings/apply/"

# Dummy Data based on Postman JSON
companies = [
    {"name": "TechNova", "email": "contact@technova.com", "username": "technova", "password": "Tech2025!"},
    {"name": "DataPulse", "email": "info@datapulse.com", "username": "datapulse", "password": "Data2025@"},
    {"name": "CloudPeak", "email": "hr@cloudpeak.com", "username": "cloudpeak", "password": "Cloud2025#"}
]

job_openings = [
    {"title": "Backend Engineer", "department": "Engineering", "location": "Remote", "status": "Pending", "postedDate": "2025-03-01", "description": "Build scalable APIs", "requirements": "Node.js, PostgreSQL", "jobType": "Full-time", "experienceLevel": "Mid", "questions": ["What is Node.js experience?", "Describe a backend project"], "benchmark": 40},
    {"title": "Frontend Developer", "department": "Engineering", "location": "Hybrid", "status": "Pending", "postedDate": "2025-03-02", "description": "Create responsive UI", "requirements": "React, TypeScript", "jobType": "Full-time", "experienceLevel": "Junior", "questions": ["React proficiency?", "UI design experience"], "benchmark": 35},
    {"title": "Data Scientist", "department": "Data", "location": "On-site", "status": "Pending", "postedDate": "2025-03-03", "description": "Analyze large datasets", "requirements": "Python, ML", "jobType": "Full-time", "experienceLevel": "Senior", "questions": ["Python skills?", "ML project example"], "benchmark": 50},
    {"title": "DevOps Engineer", "department": "Engineering", "location": "Remote", "status": "Pending", "postedDate": "2025-03-04", "description": "Manage CI/CD", "requirements": "AWS, Docker", "jobType": "Full-time", "experienceLevel": "Mid", "questions": ["AWS experience?", "CI/CD tools used"], "benchmark": 45},
    {"title": "QA Engineer", "department": "Quality", "location": "Hybrid", "status": "Pending", "postedDate": "2025-03-05", "description": "Ensure product quality", "requirements": "Selenium, JIRA", "jobType": "Full-time", "experienceLevel": "Junior", "questions": ["Selenium experience?", "Bug tracking tools"], "benchmark": 30},
    {"title": "Product Manager", "department": "Product", "location": "On-site", "status": "Pending", "postedDate": "2025-03-06", "description": "Lead product strategy", "requirements": "Agile, Roadmap", "jobType": "Full-time", "experienceLevel": "Senior", "questions": ["Agile experience?", "Roadmap planning"], "benchmark": 55},
    {"title": "UI/UX Designer", "department": "Design", "location": "Remote", "status": "Pending", "postedDate": "2025-03-07", "description": "Design user interfaces", "requirements": "Figma, Adobe XD", "jobType": "Contract", "experienceLevel": "Mid", "questions": ["Figma skills?", "UX project"], "benchmark": 40},
    {"title": "Mobile Developer", "department": "Engineering", "location": "Hybrid", "status": "Pending", "postedDate": "2025-03-08", "description": "Build mobile apps", "requirements": "Swift, Kotlin", "jobType": "Full-time", "experienceLevel": "Junior", "questions": ["Swift experience?", "Mobile app example"], "benchmark": 35},
    {"title": "Security Analyst", "department": "Security", "location": "On-site", "status": "Pending", "postedDate": "2025-03-09", "description": "Protect systems", "requirements": "Penetration testing", "jobType": "Full-time", "experienceLevel": "Senior", "questions": ["Pen testing skills?", "Security incident"], "benchmark": 50},
    {"title": "Cloud Architect", "department": "Engineering", "location": "Remote", "status": "Pending", "postedDate": "2025-03-10", "description": "Design cloud solutions", "requirements": "AWS, Azure", "jobType": "Full-time", "experienceLevel": "Senior", "questions": ["AWS expertise?", "Cloud design"], "benchmark": 60},
    {"title": "Full Stack Developer", "department": "Engineering", "location": "Hybrid", "status": "Pending", "postedDate": "2025-03-11", "description": "End-to-end development", "requirements": "MERN stack", "jobType": "Full-time", "experienceLevel": "Mid", "questions": ["MERN experience?", "Full stack project"], "benchmark": 45},
    {"title": "Machine Learning Engineer", "department": "Data", "location": "Remote", "status": "Pending", "postedDate": "2025-03-12", "description": "Develop ML models", "requirements": "TensorFlow, PyTorch", "jobType": "Full-time", "experienceLevel": "Senior", "questions": ["TensorFlow skills?", "ML model example"], "benchmark": 55},
    {"title": "Systems Administrator", "department": "IT", "location": "On-site", "status": "Pending", "postedDate": "2025-03-13", "description": "Manage servers", "requirements": "Linux, Windows", "jobType": "Full-time", "experienceLevel": "Mid", "questions": ["Linux experience?", "Server management"], "benchmark": 40},
    {"title": "Technical Writer", "department": "Documentation", "location": "Remote", "status": "Pending", "postedDate": "2025-03-14", "description": "Write technical docs", "requirements": "Markdown, API docs", "jobType": "Part-time", "experienceLevel": "Junior", "questions": ["Markdown skills?", "Doc example"], "benchmark": 30},
    {"title": "Business Analyst", "department": "Business", "location": "Hybrid", "status": "Pending", "postedDate": "2025-03-15", "description": "Gather requirements", "requirements": "BPMN, UML", "jobType": "Full-time", "experienceLevel": "Mid", "questions": ["BPMN experience?", "Requirements gathering"], "benchmark": 40},
    {"title": "Database Administrator", "department": "IT", "location": "On-site", "status": "Pending", "postedDate": "2025-03-16", "description": "Manage databases", "requirements": "SQL, NoSQL", "jobType": "Full-time", "experienceLevel": "Senior", "questions": ["SQL skills?", "DB management"], "benchmark": 50},
    {"title": "Network Engineer", "department": "IT", "location": "Hybrid", "status": "Pending", "postedDate": "2025-03-17", "description": "Maintain networks", "requirements": "Cisco, TCP/IP", "jobType": "Full-time", "experienceLevel": "Mid", "questions": ["Cisco experience?", "Network troubleshooting"], "benchmark": 45},
    {"title": "Game Developer", "department": "Engineering", "location": "Remote", "status": "Pending", "postedDate": "2025-03-18", "description": "Build games", "requirements": "Unity, Unreal", "jobType": "Full-time", "experienceLevel": "Junior", "questions": ["Unity skills?", "Game project"], "benchmark": 35},
    {"title": "AI Engineer", "department": "Data", "location": "On-site", "status": "Pending", "postedDate": "2025-03-19", "description": "Develop AI solutions", "requirements": "NLP, Deep Learning", "jobType": "Full-time", "experienceLevel": "Senior", "questions": ["NLP experience?", "AI project"], "benchmark": 60},
    {"title": "Support Engineer", "department": "Support", "location": "Hybrid", "status": "Pending", "postedDate": "2025-03-20", "description": "Assist customers", "requirements": "Ticketing systems", "jobType": "Full-time", "experienceLevel": "Junior", "questions": ["Ticketing experience?", "Support example"], "benchmark": 30},
    {"title": "Blockchain Developer", "department": "Engineering", "location": "Remote", "status": "Pending", "postedDate": "2025-03-21", "description": "Build blockchain apps", "requirements": "Solidity, Ethereum", "jobType": "Full-time", "experienceLevel": "Mid", "questions": ["Solidity skills?", "Blockchain project"], "benchmark": 45},
    {"title": "Embedded Systems Engineer", "department": "Engineering", "location": "On-site", "status": "Pending", "postedDate": "2025-03-22", "description": "Develop firmware", "requirements": "C, RTOS", "jobType": "Full-time", "experienceLevel": "Senior", "questions": ["C experience?", "Firmware example"], "benchmark": 50},
    {"title": "AR/VR Developer", "department": "Engineering", "location": "Hybrid", "status": "Pending", "postedDate": "2025-03-23", "description": "Create immersive experiences", "requirements": "Unity, VR SDKs", "jobType": "Full-time", "experienceLevel": "Mid", "questions": ["Unity VR skills?", "AR/VR project"], "benchmark": 40},
    {"title": "Site Reliability Engineer", "department": "Engineering", "location": "Remote", "status": "Pending", "postedDate": "2025-03-24", "description": "Ensure uptime", "requirements": "Monitoring, Incident response", "jobType": "Full-time", "experienceLevel": "Senior", "questions": ["Monitoring experience?", "Incident handling"], "benchmark": 55},
    {"title": "Scrum Master", "department": "Product", "location": "Hybrid", "status": "Pending", "postedDate": "2025-03-25", "description": "Facilitate Agile", "requirements": "Scrum, Kanban", "jobType": "Full-time", "experienceLevel": "Mid", "questions": ["Scrum experience?", "Agile facilitation"], "benchmark": 45}
]

applicants = [
    {"email": "alice.j@example.com", "name": "Alice J", "role": "Engineer", "status": "New"},
    {"email": "bob.s@example.com", "name": "Bob S", "role": "Developer", "status": "New"},
    {"email": "clara.l@example.com", "name": "Clara L", "role": "Analyst", "status": "New"},
    {"email": "david.k@example.com", "name": "David K", "role": "Engineer", "status": "New"},
    {"email": "emma.w@example.com", "name": "Emma W", "role": "Designer", "status": "New"},
    {"email": "frank.b@example.com", "name": "Frank B", "role": "Manager", "status": "New"},
    {"email": "grace.c@example.com", "name": "Grace C", "role": "Scientist", "status": "New"},
    {"email": "henry.d@example.com", "name": "Henry D", "role": "Engineer", "status": "New"},
    {"email": "isabella.m@example.com", "name": "Isabella M", "role": "Developer", "status": "New"},
    {"email": "james.p@example.com", "name": "James P", "role": "Analyst", "status": "New"},
    {"email": "kate.e@example.com", "name": "Kate E", "role": "Engineer", "status": "New"},
    {"email": "liam.n@example.com", "name": "Liam N", "role": "Designer", "status": "New"},
    {"email": "mia.g@example.com", "name": "Mia G", "role": "Manager", "status": "New"},
    {"email": "noah.a@example.com", "name": "Noah A", "role": "Developer", "status": "New"},
    {"email": "olivia.s@example.com", "name": "Olivia S", "role": "Engineer", "status": "New"},
    {"email": "peter.j@example.com", "name": "Peter J", "role": "Analyst", "status": "New"},
    {"email": "quinn.t@example.com", "name": "Quinn T", "role": "Scientist", "status": "New"},
    {"email": "raj.p@example.com", "name": "Raj P", "role": "Engineer", "status": "New"},
    {"email": "sophia.h@example.com", "name": "Sophia H", "role": "Developer", "status": "New"},
    {"email": "thomas.w@example.com", "name": "Thomas W", "role": "Manager", "status": "New"}
]

SKILLS_POOL = [
    "Python", "Java", "JavaScript", "React", "Node.js", "SQL", "AWS", "Docker", "Kubernetes", "Jenkins",
    "Machine Learning", "Tableau", "Power BI", "Agile", "Scrum", "Figma", "Solidity", "C", "Unity", "NLP"
]

def populate_database():
    company_tokens = []
    
    # Step 1: Register 3 companies (POST /auth/signup/)
    logger.info("Starting company registration...")
    for company in companies:
        try:
            response = requests.post(SIGNUP_URL, json=company)
            if response.status_code == 201:
                logger.info(f"Successfully registered {company['name']}")
            else:
                logger.error(f"Failed to register {company['name']}: {response.status_code} - {response.text}")
                return
        except requests.RequestException as e:
            logger.error(f"Network error registering {company['name']}: {str(e)}")
            return

    # Step 2: Login to each company (POST /auth/login/)
    logger.info("\nStarting company logins...")
    for company in companies:
        try:
            login_data = {"username": company["username"], "password": company["password"]}
            response = requests.post(LOGIN_URL, json=login_data)
            if response.status_code == 200:
                tokens = response.json()
                company_tokens.append({"company": company["name"], "access": tokens["access"]})
                logger.info(f"Successfully logged in {company['name']}")
            else:
                logger.error(f"Failed to login {company['name']}: {response.status_code} - {response.text}")
                return
        except requests.RequestException as e:
            logger.error(f"Network error logging in {company['name']}: {str(e)}")
            return

    # Step 3: Create 25 job openings (POST /openings/job-openings/)
    logger.info("\nStarting job creation...")
    job_ids = {company["name"]: [] for company in companies}
    for i, job in enumerate(job_openings):
        company = company_tokens[i % 3]
        headers = {"Authorization": f"Bearer {company['access']}"}
        try:
            response = requests.post(JOB_URL, headers=headers, json=job)
            if response.status_code == 201:
                job_id = response.json()["id"]
                job_ids[company["company"]].append(job_id)
                logger.info(f"Created '{job['title']}' for {company['company']} (ID: {job_id})")
            else:
                logger.error(f"Failed to create '{job['title']}': {response.status_code} - {response.text}")
                return
        except requests.RequestException as e:
            logger.error(f"Network error creating job '{job['title']}': {str(e)}")
            return

    # Step 4: Create 50-100 application responses (POST /openings/apply/{id}/)
    logger.info("\nStarting application responses...")
    all_job_ids = [jid for jobs in job_ids.values() for jid in jobs]
    total_applications = random.randint(50, 100)
    application_count = 0
    
    while application_count < total_applications:
        applicant = random.choice(applicants)
        job_id = random.choice(all_job_ids)
        company_name = next(company for company, ids in job_ids.items() if job_id in ids)
        headers = {"Authorization": f"Bearer {next(t['access'] for t in company_tokens if t['company'] == company_name)}"}
        
        try:
            # Fetch job details to get title
            job_response = requests.get(f"{JOB_URL}{job_id}/", headers=headers)
            if job_response.status_code != 200:
                logger.warning(f"Could not fetch job {job_id}: {job_response.status_code} - {job_response.text}")
                continue
            job_title = job_response.json()["title"]

            # Application data based on Postman "Apply-job" endpoint
            applied_date = f"2025-03-{random.randint(1, 25):02d}"
            resume_parse_data = {"text": f"Experienced in {random.choice(SKILLS_POOL)} and {random.choice(SKILLS_POOL)}"}
            app_data = {
                "name": applicant["name"],
                "email": applicant["email"],
                "role": applicant["role"],
                "status": applicant["status"],
                "score": random.randint(20, 80),
                "appliedFor": job_title,
                "appliedDate": applied_date,
                "resumeParseData": resume_parse_data
            }

            response = requests.post(f"{APPLY_URL}{job_id}/", json=app_data)
            if response.status_code == 201:
                application_count += 1
                logger.info(f"Application {application_count}/{total_applications}: {applicant['name']} applied to {job_title} (ID: {job_id})")
            else:
                logger.error(f"Failed to apply for {applicant['name']} to job ID {job_id}: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            logger.error(f"Network error applying for {applicant['name']} to job ID {job_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error applying for {applicant['name']} to job ID {job_id}: {str(e)}")

if __name__ == "__main__":
    populate_database()