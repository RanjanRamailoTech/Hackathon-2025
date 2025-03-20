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

BASE_URL = "https://ai-interview-urf8.onrender.com/"
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
    {
        "title": "Backend Engineer",
        "department": "Engineering",
        "location": "Remote",
        "status": "Pending",
        "postedDate": "2025-03-01",
        "description": "Design and maintain scalable APIs for a high-traffic application.",
        "requirements": "Node.js, PostgreSQL, RESTful API design",
        "jobType": "Full-time",
        "experienceLevel": "Mid",
        "questions": [
            "How do you ensure API scalability under heavy load?",
            "What strategies do you use for database optimization in PostgreSQL?",
            "Can you explain how you’ve implemented authentication in a past project?",
            "Describe a challenging bug you encountered in a backend system and how you resolved it.",
            "How do you handle versioning in RESTful APIs?",
            "What’s your experience with microservices architecture?",
            "How do you ensure data consistency across distributed systems?"
        ],
        "benchmark": 40
    },
    {
        "title": "Frontend Developer",
        "department": "Engineering",
        "location": "Hybrid",
        "status": "Pending",
        "postedDate": "2025-03-02",
        "description": "Develop responsive and interactive user interfaces for web applications.",
        "requirements": "React, TypeScript, CSS",
        "jobType": "Full-time",
        "experienceLevel": "Junior",
        "questions": [
            "How do you optimize React components for performance?",
            "What’s the difference between controlled and uncontrolled components in React?",
            "Can you explain how you’ve used TypeScript to improve code quality?",
            "How do you ensure cross-browser compatibility in your projects?",
            "Describe a time you had to debug a complex UI issue.",
            "What’s your approach to managing state in a React application?",
            "How do you handle responsive design in CSS?"
        ],
        "benchmark": 35
    },
    {
        "title": "Data Scientist",
        "department": "Data",
        "location": "On-site",
        "status": "Pending",
        "postedDate": "2025-03-03",
        "description": "Analyze large datasets to derive actionable business insights.",
        "requirements": "Python, Machine Learning, Statistics",
        "jobType": "Full-time",
        "experienceLevel": "Senior",
        "questions": [
            "How do you select the right machine learning model for a given problem?",
            "Describe a time you used Python to clean and preprocess messy data.",
            "What’s your approach to feature engineering?",
            "Can you explain a project where you improved model accuracy?",
            "How do you evaluate the performance of a regression model?",
            "What’s your experience with deploying ML models into production?",
            "How do you handle imbalanced datasets?",
            "What statistical methods do you use to validate your findings?"
        ],
        "benchmark": 50
    },
    {
        "title": "DevOps Engineer",
        "department": "Engineering",
        "location": "Remote",
        "status": "Pending",
        "postedDate": "2025-03-04",
        "description": "Manage CI/CD pipelines and cloud infrastructure.",
        "requirements": "AWS, Docker, Jenkins",
        "jobType": "Full-time",
        "experienceLevel": "Mid",
        "questions": [
            "How do you set up a CI/CD pipeline using Jenkins?",
            "What’s your experience with container orchestration using Docker?",
            "Can you describe a time you resolved a production outage?",
            "How do you monitor AWS infrastructure for performance issues?",
            "What’s your approach to securing cloud resources?",
            "How do you automate infrastructure provisioning?",
            "Describe a challenging deployment you managed."
        ],
        "benchmark": 45
    },
    {
        "title": "QA Engineer",
        "department": "Quality",
        "location": "Hybrid",
        "status": "Pending",
        "postedDate": "2025-03-05",
        "description": "Ensure product quality through manual and automated testing.",
        "requirements": "Selenium, JIRA, Test Automation",
        "jobType": "Full-time",
        "experienceLevel": "Junior",
        "questions": [
            "How do you write effective test cases for a web application?",
            "What’s your experience with Selenium for automated testing?",
            "Can you explain how you prioritize bugs in JIRA?",
            "Describe a time you caught a critical defect before release.",
            "How do you approach testing a new feature?",
            "What’s the difference between black-box and white-box testing?",
            "How do you ensure test coverage in an agile environment?"
        ],
        "benchmark": 30
    },
    {
        "title": "Product Manager",
        "department": "Product",
        "location": "On-site",
        "status": "Pending",
        "postedDate": "2025-03-06",
        "description": "Define and execute product strategy for a SaaS platform.",
        "requirements": "Agile, Roadmap Planning, Stakeholder Management",
        "jobType": "Full-time",
        "experienceLevel": "Senior",
        "questions": [
            "How do you prioritize features for a product roadmap?",
            "Describe a time you managed conflicting stakeholder requirements.",
            "What’s your approach to running an Agile sprint?",
            "Can you explain a product launch you led from start to finish?",
            "How do you measure the success of a product feature?",
            "What tools do you use for product backlog management?",
            "How do you gather and incorporate user feedback?",
            "Describe a time you pivoted a product strategy based on data."
        ],
        "benchmark": 55
    },
    {
        "title": "UI/UX Designer",
        "department": "Design",
        "location": "Remote",
        "status": "Pending",
        "postedDate": "2025-03-07",
        "description": "Design intuitive and visually appealing user interfaces.",
        "requirements": "Figma, Adobe XD, User Research",
        "jobType": "Contract",
        "experienceLevel": "Mid",
        "questions": [
            "How do you conduct user research for a new design?",
            "What’s your process for creating wireframes in Figma?",
            "Can you describe a time you improved usability based on feedback?",
            "How do you ensure accessibility in your designs?",
            "What’s your experience with prototyping in Adobe XD?",
            "How do you collaborate with developers to implement designs?",
            "Describe a challenging design project and your solution."
        ],
        "benchmark": 40
    },
    {
        "title": "Mobile Developer",
        "department": "Engineering",
        "location": "Hybrid",
        "status": "Pending",
        "postedDate": "2025-03-08",
        "description": "Develop and maintain iOS and Android applications.",
        "requirements": "Swift, Kotlin, Mobile UI",
        "jobType": "Full-time",
        "experienceLevel": "Junior",
        "questions": [
            "How do you optimize a mobile app for performance?",
            "What’s your experience with Swift for iOS development?",
            "Can you explain a time you debugged a mobile app crash?",
            "How do you handle different screen sizes in Android with Kotlin?",
            "What’s your approach to integrating APIs in a mobile app?",
            "Describe a mobile app you’ve built from scratch."
        ],
        "benchmark": 35
    },
    {
        "title": "Security Analyst",
        "department": "Security",
        "location": "On-site",
        "status": "Pending",
        "postedDate": "2025-03-09",
        "description": "Identify and mitigate security risks in IT systems.",
        "requirements": "Penetration Testing, Cybersecurity Frameworks",
        "jobType": "Full-time",
        "experienceLevel": "Senior",
        "questions": [
            "How do you conduct a penetration test on a web application?",
            "Describe a security vulnerability you discovered and fixed.",
            "What’s your experience with OWASP Top 10 vulnerabilities?",
            "How do you stay updated on the latest cybersecurity threats?",
            "Can you explain how you’d respond to a data breach?",
            "What tools do you use for security audits?",
            "How do you ensure compliance with GDPR or similar regulations?",
            "Describe a time you trained a team on security best practices."
        ],
        "benchmark": 50
    },
    {
        "title": "Cloud Architect",
        "department": "Engineering",
        "location": "Remote",
        "status": "Pending",
        "postedDate": "2025-03-10",
        "description": "Design and oversee cloud infrastructure solutions.",
        "requirements": "AWS, Azure, Cloud Security",
        "jobType": "Full-time",
        "experienceLevel": "Senior",
        "questions": [
            "How do you design a highly available cloud architecture?",
            "What’s your experience with AWS multi-region deployments?",
            "Can you explain a cost-optimization strategy you implemented in Azure?",
            "How do you secure sensitive data in a cloud environment?",
            "Describe a time you migrated an on-premise system to the cloud.",
            "What’s your approach to disaster recovery in the cloud?",
            "How do you evaluate cloud providers for a specific use case?",
            "What tools do you use for cloud infrastructure monitoring?"
        ],
        "benchmark": 60
    },
    {
        "title": "Full Stack Developer",
        "department": "Engineering",
        "location": "Hybrid",
        "status": "Pending",
        "postedDate": "2025-03-11",
        "description": "Develop end-to-end solutions for web applications.",
        "requirements": "MERN Stack (MongoDB, Express.js, React, Node.js)",
        "jobType": "Full-time",
        "experienceLevel": "Mid",
        "questions": [
            "How do you structure a MERN stack application?",
            "What’s your experience with MongoDB indexing for performance?",
            "Can you explain a time you integrated a third-party API?",
            "How do you ensure security in a full-stack application?",
            "Describe a full-stack project you’ve completed.",
            "What’s your approach to testing both frontend and backend?",
            "How do you handle state management in React?"
        ],
        "benchmark": 45
    },
    {
        "title": "Machine Learning Engineer",
        "department": "Data",
        "location": "Remote",
        "status": "Pending",
        "postedDate": "2025-03-12",
        "description": "Build and deploy machine learning models for predictive analytics.",
        "requirements": "TensorFlow, PyTorch, Data Pipelines",
        "jobType": "Full-time",
        "experienceLevel": "Senior",
        "questions": [
            "How do you choose between TensorFlow and PyTorch for a project?",
            "Describe a time you optimized a neural network’s performance.",
            "What’s your experience with building data pipelines?",
            "How do you deploy a machine learning model to production?",
            "Can you explain a time you dealt with overfitting?",
            "What’s your approach to hyperparameter tuning?",
            "How do you validate the accuracy of a predictive model?",
            "Describe a challenging ML project and its outcome."
        ],
        "benchmark": 55
    },
    {
        "title": "Systems Administrator",
        "department": "IT",
        "location": "On-site",
        "status": "Pending",
        "postedDate": "2025-03-13",
        "description": "Manage and maintain server infrastructure.",
        "requirements": "Linux, Windows Server, Networking",
        "jobType": "Full-time",
        "experienceLevel": "Mid",
        "questions": [
            "How do you troubleshoot a server outage in Linux?",
            "What’s your experience with Windows Server administration?",
            "Can you describe a time you improved server performance?",
            "How do you configure a secure network for internal systems?",
            "What’s your approach to patch management?",
            "How do you back up critical server data?",
            "Describe a time you resolved a network connectivity issue."
        ],
        "benchmark": 40
    },
    {
        "title": "Technical Writer",
        "department": "Documentation",
        "location": "Remote",
        "status": "Pending",
        "postedDate": "2025-03-14",
        "description": "Create clear and concise technical documentation.",
        "requirements": "Markdown, API Documentation, Technical Communication",
        "jobType": "Part-time",
        "experienceLevel": "Junior",
        "questions": [
            "How do you write user-friendly API documentation?",
            "What’s your experience with Markdown for technical docs?",
            "Can you describe a time you simplified complex technical content?",
            "How do you collaborate with developers to gather information?",
            "What tools do you use for documentation versioning?",
            "Describe a documentation project you’re proud of."
        ],
        "benchmark": 30
    },
    {
        "title": "Business Analyst",
        "department": "Business",
        "location": "Hybrid",
        "status": "Pending",
        "postedDate": "2025-03-15",
        "description": "Analyze business needs and document requirements.",
        "requirements": "BPMN, UML, Stakeholder Analysis",
        "jobType": "Full-time",
        "experienceLevel": "Mid",
        "questions": [
            "How do you create a BPMN diagram for a business process?",
            "What’s your experience with UML for system modeling?",
            "Can you explain a time you bridged a gap between stakeholders?",
            "How do you prioritize requirements in a project?",
            "Describe a challenging requirement-gathering session.",
            "What’s your approach to validating business requirements?",
            "How do you handle scope creep in a project?"
        ],
        "benchmark": 40
    }
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