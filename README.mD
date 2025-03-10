# Smart HR - AI-Powered Recruitment Platform

## Project Overview

Smart HR is a cutting-edge, AI-powered recruitment platform designed to revolutionize the hiring process for small-to-medium enterprises (SMEs) and large organizations alike. By integrating artificial intelligence into every stage of recruitment—from job creation to candidate evaluation—Smart HR reduces hiring timelines by over 60%, eliminates manual overhead, and ensures unbiased candidate selection. The platform leverages advanced natural language processing (NLP), speech recognition, and machine learning to deliver a seamless, data-driven experience for recruiters and job seekers.

### Key Features

- **Automated Job Creation**: Companies can input basic job requirements or skill-specific questions, and the system generates detailed job postings with descriptions, requirements, and custom interview questions using AI models.
- **Candidate Screening**: AI parses resumes, extracts technical keywords, and scores applicants against predefined job benchmarks, filtering out unqualified candidates automatically.
- **AI-Driven Interviews**: Conducts asynchronous video interviews, transcribes responses in real-time, and evaluates candidates based on verbal and non-verbal cues, aligning answers with job requirements.
- **Comprehensive Reporting**: Generates detailed evaluation reports with scores, strengths, weaknesses, and hiring recommendations, empowering recruiters with actionable insights.
- **Scalable SaaS Model**: Offers a subscription-based pricing structure with tiered plans (e.g., Basic, Pro, Enterprise) to cater to businesses of all sizes, with features like multi-user access and analytics dashboards.
- **Real-Time Collaboration**: Supports live monitoring and feedback during interviews via WebSocket integration, enabling team collaboration.

### Application Details

- **Target Audience**: HR departments, recruitment agencies, and tech-driven companies seeking efficient hiring solutions.
- **Value Proposition**: Combines automation and AI to reduce time-to-hire, improve candidate quality, and lower recruitment costs.
- **Scalability**: Built with a modular Django backend, allowing easy integration of new features like multilingual support or advanced analytics.
- **Security**: Implements JWT-based authentication, role-based access control (RBAC), and secure file handling for sensitive applicant data.
- **Extensibility**: Open to third-party integrations (e.g., LinkedIn for candidate sourcing, Slack for notifications) via API hooks.

### Technology Stack

- **Backend**: Django (Python) with REST Framework
- **Database**: PostgreSQL for relational data storage
- **Frontend**: React (assumed, not provided in code) for a responsive UI
- **AI/ML**: OpenAI Whisper for speech-to-text, GPT models for text generation and evaluation
- **Automation**: N8N (assumed) for workflow orchestration
- **Real-Time**: Django Channels with Redis for WebSocket support
- **Media Processing**: FFmpeg for audio extraction from video interviews

### Application Flow

The Smart HR platform follows a structured workflow that integrates company actions, candidate interactions, and AI-driven processing:

1. **Company Registration & Job Creation**

   - A company registers via the signup API (`/api/auth/signup/`) and logs in (`/api/auth/login/`).
   - The company creates a job opening (`/api/job-openings/`) with details like title, requirements, and benchmark score. The system auto-generates an application link.

2. **Candidate Application**

   - Candidates discover job openings publicly (`/api/job-openings-public/<id>/`) and apply (`/api/apply/<jobId>/`) with their resume and details.
   - The system parses the resume, extracts keywords, scores the applicant against the benchmark, and notifies them via email (acceptance with interview link or rejection).

3. **Interview Process**

   - Accepted candidates start an interview (`/api/start-interview/`), receiving a WebSocket URL for real-time interaction.
   - During the interview, video/audio chunks are sent via WebSocket (`ws://<host>/ws/video/<room_key>/`). The system transcribes audio, extracts QA pairs, and evaluates responses.

4. **Evaluation & Reporting**

   - Interview videos are processed (`/api/process/`) to score responses against job criteria. Scores are stored and aggregated.
   - When complete (`final_flag: true`), a final report is generated with overall scores, strengths, and recommendations.
   - Recruiters access the report (`/api/report/<applicant_response_id>/`) to make hiring decisions.

5. **Dashboard & Analytics**
   - Companies monitor progress via the dashboard (`/api/dashboard/`) and review all applicants (`/api/dashboard/total-applicant/`), enabling data-driven hiring.

This flow ensures a fully automated, end-to-end recruitment process with minimal human intervention, leveraging AI for efficiency and accuracy.

---

## Backend Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- FFmpeg (for audio extraction)
- Redis (for Django Channels)
- OpenAI API Key
- SMTP Server (e.g., Gmail for email notifications)

### Installation Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/RanjanRamailoTech/video-conf.git
   cd video-conf
   ```
2. **Set Up Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txtf
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the project root:
   ```bash
   EMAIL_HOST_USER=Your_email
   GMAIL_APP_PASS=Your_app_password
   OPEN_AI_KEY=Your_Openai_API_Key
   DB_NAME=Your_DB_Name
   DB_USER=Your_DB_User
   DB_PASSWORD=Your_DB_Password
   DB_HOST=Your_DB_Host
   DB_PORT=Your_DB_Port
   ```
5. **Database Setup Initialize the database:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```

The backend server will be running at `127.0.0.1:8000` (BASEURL)

## API Documentation

This section provides detailed documentation for all APIs in the Smart HR backend. Each endpoint includes its purpose, HTTP method, URL, request payload (if applicable), and response structure.

### Authentication APIs

1. **Company Signup:**
   Registers a new company user.

- Method: `POST`

* URL: `/BASEURL/auth/signup/`

- Permissions: Public (AllowAny)
- Payload:

```
{
"username": "company1",
"email": "company@example.com",
"password": "securepassword123",
"company_name": "Example Corp"
}
```

- Response

  - Success (201 Created):

  ```
  {
  "message": "Company registered successfully",
  "company_id": 1
  }
  ```

  - Error (400 Bad Request):

  ```
  {
  "message": "Company registered successfully",
  "company_id": 1
  }
  ```

2. **Company Login:**
   Authenticates a company user and returns JWT tokens.

- Method: `POST`

* URL: `/BASEURL/auth/login/`

- Permissions: Public (AllowAny)
- Payload:

```
{
  "username": "company1",
  "password": "securepassword123"
}
```

- Response

  - Success (200 OK):

  ```
    {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  ```

  - Error (401 Unauthorized):

  ```
  {
  "error": "Invalid credentials"
  }
  ```

  - Error (400 Bad Request):

  ```
  {
  "username": ["This field is required."]
  }
  ```

### Job Opening APIs

3. **List/Create Job Openings:**
   Lists all job openings for the authenticated company or creates a new one.

- Method: `GET`/`POST`

* URL: `/BASEURL/auth/signup/`

- Permissions: Authenticated
  Headers: `Authorization: Bearer <access_token>`
- GET Response:

  - Success (200 OK):
    ```
    [{
    "id": 1,
    "title": "Backend Engineer",
    "department": "Engineering",
    "location": "Remote",
    "applicants": 5,
    "status": "Active",
    "postedDate": "2025-03-10",
    "description": "Develop APIs...",
    "requirements": "3+ years Python...",
    "jobType": "Full-time",
    "experienceLevel": "Mid",
    "questions": ["How do you optimize APIs?"],
    "application_link": "http://localhost:8000/api/apply/1/",
    "benchmark": 40
    }]
    ```

- POST Response:

  - Success (201 Created):
    ```
    {
    "id": 2,
    "title": "Frontend Developer",
    "application_link": "http://localhost:8000/api/apply/2/",
    "department": "Engineering",
    "location": "Remote",
    "applicants": 0,
    "status": "Active",
    "postedDate": "2025-03-10",
    "description": "Build UIs...",
    "requirements": "React experience...",
    "jobType": "Full-time",
    "experienceLevel": "Junior",
    "questions": ["What is a component?"],
    "benchmark": 30
    }
    ```
  - Error (400 Bad Request):
    ```
    {
    "title": ["This field is required."]
    }
    ```

4. **Job Opening Detail:**
   Retrieves, updates, or deletes a specific job opening.

- Method: `GET`/`POST`/`DELETE`

* URL: `/BASEURL/job-openings/<id>/`

- Permissions: Authenticated

* Headers: `Authorization: Bearer <access_token>`

- GET Response:

  - Succcess (200 OK)

  ```
  {
  "id": 1,
  "title": "Backend Engineer",
  "department": "Engineering",
  "location": "Remote",
  "applicants": 5,
  "status": "Active",
  "postedDate": "2025-03-10",
  "description": "Develop APIs...",
  "requirements": "3+ years Python...",
  "jobType": "Full-time",
  "experienceLevel": "Mid",
  "questions": ["How do you optimize APIs?"],
  "application_link": "http://localhost:8000/api/apply/1/",
  "benchmark": 40
  }
  ```

  - Error (404 Not Found):

  ```
  {
  "error": "Job opening not found"
  }
  ```

- Put Payload:

```
{
  "status": "Archived"
}
```

- Put Response

  - Success (200 OK)

  ```
    {
    "id": 1,
    "title": "Backend Engineer",
    "status": "Archived",
    "department": "Engineering",
    "location": "Remote",
    "applicants": 5,
    "postedDate": "2025-03-10",
    "description": "Develop APIs...",
    "requirements": "3+ years Python...",
    "jobType": "Full-time",
    "experienceLevel": "Mid",
    "questions": ["How do you optimize APIs?"],
    "application_link": "http://localhost:8000/api/apply/1/",
    "benchmark": 40
  }
  ```

  - Error (400 Bad Request):

  ```
  {
  "status": ["Invalid choice."]
  }
  ```

- DELETE Response

  - Success (200 OK): No Body
  - Error (400 Bad Request):

  ```
  {
  "status": ["Invalid choice."]
  }
  ```

5.  **Public Job Opening Detail:**
    Retrieves public details of a job opening.

- Method: `GET`

* URL: `/BASEURL/job-openings-public/<id>/`

- Permissions: Public (AllowAny)

- Response

  - Success (200 OK):

  ```
  {
  "id": 1,
  "title": "Backend Engineer",
  "department": "Engineering",
  "location": "Remote",
  "postedDate": "2025-03-10",
  "description": "Develop APIs...",
  "requirements": "3+ years Python...",
  "jobType": "Full-time",
  "experienceLevel": "Mid",
  "application_link": "http://localhost:8000/api/apply/1/"
  }
  ```

  - Error (404 Not Found):

  ```
    {
    "error": "Job opening not found"
    }

  ```

6.  **Apply to Job Opening:**
    Submits an applicant response to a job opening.

- Method: `POST`

* URL: `/BASEURL/apply/<jobId>/`

- Permissions: Public (AllowAny)
- Payload:

```
{
  "name": "John Doe",
  "role": "Backend Engineer",
  "score": 50,
  "appliedFor": "Backend Engineer",
  "appliedDate": "2025-03-10",
  "resumeParseData": {"skills": ["Python", "Django"]},
  "email": "john@example.com"
}

```

- Response

  - Success (201 Created):

  ```
  {
  "id": 1,
  "jobId": 1,
  "name": "John Doe",
  "role": "Backend Engineer",
  "score": 50,
  "appliedFor": "Backend Engineer",
  "appliedDate": "2025-03-10",
  "email": "john@example.com",
  "interview_id": 1  // Included if score >= benchmark
  }
  ```

  - Error (400 Bad Request):

  ```
  {
  "email": ["This field is required."]
  }
  ```

7.  **List Applicant Responses:**
    Lists all applicant responses for a specific job.

- Method: `GET`

* URL: `/BASEURL/dashboard/job-openings/<jobId>/responses/`

- Permissions: Authenticated

* Headers: `Authorization: Bearer <access_token>`

- Response

  - Success (200 OK):

  ```
  [
  {
    "id": 1,
    "jobId": 1,
    "name": "John Doe",
    "role": "Backend Engineer",
    "score": 50,
    "appliedFor": "Backend Engineer",
    "appliedDate": "2025-03-10",
    "email": "john@example.com"
  }
  ]
  ```

  - Error (404 Not Found):

  ```
  {
  "error": "Job opening not found or not owned by this company"
  }
  ```

8.  **Applicant Response Detail:**
    Retrieves details of a specific applicant response.

- Method: `GET`

* URL: `/BASEURL/dashboard/job-openings/<jobId>/responses/<responseId>/1`

- Permissions: Authenticated

* Headers: `Authorization: Bearer <access_token>`

- Response

  - Success (200 OK):

  ```
    {
  "id": 1,
  "jobId": 1,
  "name": "John Doe",
  "role": "Backend Engineer",
  "score": 50,
  "appliedFor": "Backend Engineer",
  "appliedDate": "2025-03-10",
  "email": "john@example.com"
  }
  ```

  - Error (404 Not Found):

  ```
    {
  "error": "Response not found for this job opening"
  }
  ```

9.  **Company Dashboard Stats:**
    Retrieves statistical data for the company dashboard.

- Method: `GET`

* URL: `/BASEURL/dashboard/`

- Permissions: Authenticated

* Headers: `Authorization: Bearer <access_token>`

- Response

  - Success (200 OK):

  ```
  {
  "job_openings": 5,
  "total_candidates": 20,
  "interviews_in_progress": 3
  }
  ```

  - Error (404 Not Found):

  ```
    {
    "error": "Company not found for this user"
    }
  ```

10. **Total Applicant Responses:**
    Lists all applicant responses across all company jobs.

- Method: `GET`

* URL: `/BASEURL/dashboard/total-applicant/`

- Permissions: Authenticated

* Headers: `Authorization: Bearer <access_token>`

- Response

  - Success (200 OK):

  ```
  [
  {
    "id": 1,
    "jobId": 1,
    "name": "John Doe",
    "role": "Backend Engineer",
    "score": 50,
    "appliedFor": "Backend Engineer",
    "appliedDate": "2025-03-10",
    "email": "john@example.com"
  }
  ]
  ```

  - Error (404 Not Found):

  ```
    {
  "error": "Company not found for this user"
  }
  ```

11. **Job Opening Questions:**
    Retrieves the questions associated with a job opening.

- Method: `GET`

* URL: `/BASEURL/questions/<jobId>/`

- Permissions: Public (AllowAny)
- Payload:

```

{
"username": "company1",
"email": "company@example.com",
"password": "securepassword123",
"company_name": "Example Corp"
}

```

- Response

  - Success (200 OK):

  ```
  {
  "questions": ["How do you optimize APIs?"]
  }
  ```

  - Error (404 Not Found):

  ```
  {
  "error": "Job opening not found"
  }
  ```

### Interview APIs

12. **Process Interview:**
    Processes an uploaded interview video to extract and score responses.

- Method: `POST`

* URL: `/BASEURL/call/process/`

- Permissions: Public (AllowAny)

* Query Params: `?interview_id=<id>`

- Payload (multipart/form-data):

```
Content-Type: multipart/form-data
video_file: <file_upload> (e.g., interview.mp4)
question: "How do you optimize APIs?"
final_flag: true  // Optional, default: false
```

- Response

  - Success (200 OK):

  ```
  {
  "message": "Video processed successfully"
  }
  ```

  - Error (400 Bad Request):

  ```
  {
  "error": "video_file is required"
  }
  ```

  - Error (500 Internal Server Error):

  ```
  {
  "error": "Processing failed",
  "traceback": "..."
  }
  ```

13. **Interview Report:**
    Retrieves the evaluation report for an applicant response.

- Method: `POST`

* URL: `/BASEURL/report/<applicant_response_id>/`

- Permissions: Authenticated

* Headers: `Authorization: Bearer <access_token>`

- Response:

  - Success (200 OK):

  ```
  {
  "data": {
    "interview": 1,
    "verbal_scores": {"How do you optimize APIs?": "7.5"},
    "final_report": {
      "Overall Score": "7.5/1",
      "Strengths": "Technical accuracy",
      "Key Skill Gaps": "Communication clarity",
      "Communication Skills": "Decent articulation; lacks job specificity",
      "Recommendation": "Do not progress"
    }
  }
  }
  ```

  - Error (400 Bad Request):

  ```
  {
  "error": "Candidate application doesn't exist"
  }
  ```
