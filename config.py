"""
Configuration for the Job Scan Flask app.

- Fixed resume text used for all comparisons
- Job categories to search
- Crawler limits and timeouts
"""

import os


# Fixed resume text used for comparisons.
# Replace this with your own resume content.
RESUME_TEXT = os.environ.get(
    "JOBSCAN_RESUME_TEXT",
    """
Jason Wiggs 
jason.wiggs@outlook.com | 773-841-2363
Chicago, IL + New York, NY + Remote
https://www.linkedin.com/in/jason-wiggs
Job Title From Job Description Goes Here
Software Development | Artificial Intelligence, LLM | Salesforce | Python, Java, Apex
Innovative and flexible Senior Software Engineer with a master’s degree in computer science and 11+ years of experience in software development, including AI chat implementations, Salesforce CRM development, REST API integrations, mainframe tools and applications, and mobile browser quality assurance, seeking a role creating secure solutions using new and emerging tech in a fast-paced, team-focused environment.

Expert in Agile methods and test-driven development, actively learning and implementing new technologies.
Collaborative, detail-oriented, able to work independently, follow instructions, and complete projects on time.
Expertise in coding programs, feature development, bug fixes, collaborating with IT and stakeholder teams, and contributing to codebase and pipeline improvements across multiple platforms and frameworks.
Outstanding analytical, technical, prioritization, problem-solving, typing, writing, and time-management skills.

SKILLS
Programming:
Python, Java, C++, Apex, Groovy, JSON, Javascript, HTML, SQL, Assembler, ISPF
Tools:
Git, GitHub, Selenium, REST APIs, AWS Servers (EC2), Jira, Jenkins, MySQL, SQL Server, Microsoft Office Suite, JIRA; Familiar with Docker, Django, NoSQL
Experience:
Software Engineering, Debugging, Unit Testing, Application Development, Version Control Systems, Microservices, Software Development Lifecycle (SDLC), Continuous Integration/Continuous Deployment (CI/CD), Automated Testing, Quality Assurance, Technical Documentation, Agile Development and Scrum, Software Development Process, Algorithms, Data Structures, Test-Driven Development, Cloud Technologies, Refactoring, Kanban, Scrum, Relational Databases, Object-Oriented Programming
Select Projects:
Web security audit: Sought security vulnerabilities via URL parameters in web applications.
Data Transmission: Wrote iPhone display application for local, not-for-profit CHIRP Radio.
Mobile app development: Wrote iPhone app displaying activities and sights for travelers.
GitHub:
https://github.com/wiggs30

WORK EXPERIENCE
Senior Software Engineer | Senior Application Developer 
Revenova, Chicago, IL - 06/2023 – 05/2024
Revenova is the leading provider of CRM-powered transportation management systems (TMS) for third-party logistics (3PLs) companies, freight brokers, trucking companies, and shippers built natively on Salesforce Cloud.
Designed and implemented custom features and product improvements on client-specific instances of the TMS using JavaScript, CSS, Salesforce’s Apex language, and No Code/Low Code tools, and verified all changes through Unit Testing required for deployment.
Significantly reduced transaction costs for customers by refactoring the Apex batch job code to decrease the number of API calls by 80% to stay underneath contracted data limits.
Addressed technical issues reported by customers by assisting product managers with technical knowledge and solutions.
Improved client and engineering team’s knowledge of the TMS product by documenting solutions and uploading them to the company Wiki.
Maintained growing code base in repository for reuse and application improvement.
Participated in daily cross-functional requirements gathering meetings for feature design and implementation.
Cognitive Implementation Technical Lead | Artificial Intelligence Implementation Engineer | Applied AI Lead
IPSoft, Chicago, IL – 06/2017 – 12/2022  
Hired and led a team of nine developers designing, building, and implementing conversational solutions on the Amelia SaaS platform, a cloud-based AI chat interface utilizing natural language processing (NLP) and early large language model technology.
Trained AI for natural language processing (NLP) by collating training data from client SME and creating a client-specific large language model (LLM) classifier to improve the user experience.
Directed continuous integration for user testing and production updates by designing a business process to verify and collect the team sprint changes and advancing the updates through test, staging, and production.
Served as Sales Engineer to demonstrate Amelia AI product functionality and architecture to clients in post-sales implementation meetings.
Installed and configured platform software on clients' AWS cloud servers.
Trained AI for natural language processing (NLP) by collating training data from client SME and creating a client-specific large language model (LLM) classifier to improve the user experience.
Improved user outcome success rates to 90%+ goal by building a Python script to analyze user conversations for performance metrics.
Mentored all engineers on company business processes and implementation of intent models.
Built high-quality software experiences for customers by collaborating on product needs and requirements.

Software Engineer
CA Technologies, Lisle, IL – 06/2013 – 03/2017  
Worked with a team of four to six engineers to design and implement IBM Mainframe tools used by database administrators.
Developed and maintained enterprise-level IBM mainframe applications using Assembler code.
Built Java application for querying databases to assist DBAs in using less SQL.
Created automated tests in Python and Selenium to regularly test our products, reducing testing time by 50%.

Quality Assurance Engineer
Nokia (formerly Novarra), Itasca, IL – 05/2008 – 05/2012  
Developed automated testing suites to rigorously test software designed for mobile devices.
Worked with a team to complete software packages by client deadlines.
Used mobile and desktop computer systems intensively to improve application quality.

EDUCATION
Master of Science, MS, Computer Science, University of Illinois - Chicago, Chicago, IL
Bachelor's Degree, Economics, University of Illinois - Chicago, Chicago, IL
""",
)


# Job categories to search across all sites.
JOB_CATEGORIES = [
    "software engineer",
    "software developer",
    "implementation engineer",
    "forward deployed engineer",
    "python developer",
    "java developer",
    "backend developer",
    "senior software engineer",
    "senior software developer",
    "senior implementation engineer",
    "senior python developer",
    "senior java developer",
    "senior backend developer",
]


# Crawler limits to avoid hammering sites.
MAX_JOBS_PER_CATEGORY_PER_SITE = int(os.environ.get("MAX_JOBS_PER_CATEGORY_PER_SITE", 10))
#MAX_JOBS_PER_CATEGORY_PER_SITE = int(os.environ.get("MAX_JOBS_PER_CATEGORY_PER_SITE", 5))
MAX_JOBS_TOTAL = int(os.environ.get("MAX_JOBS_TOTAL", 100))
#MAX_JOBS_TOTAL = int(os.environ.get("MAX_JOBS_TOTAL", 50))

# HTTP settings for crawlers.
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 15))
CRAWL_DELAY = float(os.environ.get("CRAWL_DELAY", 2.0))


# Optional JobScan login (if required by the site).
JOBSCAN_EMAIL = os.environ.get("JOBSCAN_EMAIL", "")
JOBSCAN_PASSWORD = os.environ.get("JOBSCAN_PASSWORD", "")

