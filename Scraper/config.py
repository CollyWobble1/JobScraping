"""
Configuration for the TimesJobs scraper.

Edit this file to change search terms, output locations, or the keyword
list — you should not need to touch scraper.py for routine changes.
"""

# ---------------------------------------------------------------------------
# Search settings
# ---------------------------------------------------------------------------

SEARCH_KEYWORD = "software engineer"   # What to search for on TimesJobs
MAX_PAGES = 1000                       # Safety cap on how many search-result pages to crawl.
                                        # TimesJobs will run out of real results long before this,
                                        # so it mostly exists to stop an infinite loop if something
                                        # goes wrong upstream.

# ---------------------------------------------------------------------------
# Output file
# ---------------------------------------------------------------------------
# Single CSV, written incrementally (one row at a time, fully complete —
# card fields + skills + keywords all together) so a crash or a manual
# Ctrl+C never loses more than the single job in progress.

FINAL_CSV = "timesjobs_final.csv"     # title, company, url, location, experience, salary, skills, keywords
LOG_FILE = "scrape_log.txt"           # Timestamped run log, useful for checking what happened overnight

# ---------------------------------------------------------------------------
# Resilience / rate-limiting settings
# ---------------------------------------------------------------------------

PAGE_LOAD_WAIT_SECONDS = 10     # How long to wait for search-result cards to appear before giving up
BETWEEN_PAGE_DELAY = 2          # Pause between search-result page loads (politeness)
BETWEEN_DETAIL_DELAY = 2        # Pause between individual job detail-page loads (politeness)
EMPTY_PAGE_BACKOFF = 5          # Extra pause after a page comes back with zero cards, before retrying

NO_NEW_JOBS_PAGE_LIMIT = 3      # Stop the run after this many consecutive search pages produce
                                 # ZERO new completed jobs — whether because the page had no cards
                                 # at all, or because every card on it was a duplicate we'd already
                                 # scraped (this second case is what catches a broken pagination
                                 # parameter, which would otherwise loop forever re-scraping the
                                 # same first page).

CONSECUTIVE_SKILL_FAILURE_LIMIT = 15   # Stop the run after this many detail pages in a row come back
                                        # with no skills found — likely means TimesJobs changed its
                                        # page layout, or we're being blocked, and continuing would
                                        # just produce hours of empty/garbage rows.

# ---------------------------------------------------------------------------
# Keyword list for scanning job descriptions
# ---------------------------------------------------------------------------
# Matching is whole-word (see scraper.find_matched_keywords), so "Go" will not
# false-match inside "Google", and "Unity" will not false-match inside
# "opportunity". Trim or extend freely — this has no effect on selector logic.

KEYWORDS_TO_FLAG = [
    # Languages
    "C++", "C#", "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust",
    "Kotlin", "Swift", "PHP", "Ruby", "Scala", "R", "MATLAB", "Perl",
    "Objective-C", "Dart", "Lua", "Haskell", "Assembly",

    # Web / frontend
    "React", "Angular", "Vue", "Next.js", "HTML", "CSS", "Tailwind",
    "Node.js", "Express", "GraphQL", "REST API", "WebSocket", "jQuery",

    # Backend frameworks
    "Django", "Flask", "FastAPI", "Spring", "Spring Boot", ".NET", "ASP.NET",
    "Ruby on Rails", "Laravel",

    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
    "Terraform", "Ansible", "Jenkins", "CI/CD", "GitHub Actions",
    "Serverless", "Lambda", "Nginx", "Linux", "Bash", "Shell Scripting",

    # Databases
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
    "Cassandra", "DynamoDB", "Elasticsearch", "Firebase", "NoSQL",

    # Data / ML / AI
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
    "Scikit-learn", "Pandas", "NumPy", "Data Science", "NLP",
    "Computer Vision", "OpenCV", "Hugging Face", "LLM", "Generative AI",
    "Data Engineering", "ETL", "Apache Spark", "Kafka", "Airflow",

    # Game development
    "Unity", "Unreal Engine", "Godot", "Blueprint",
    "OpenGL", "DirectX", "Vulkan", "Shader", "HLSL", "GLSL",
    "Blender", "Maya", "3D Modeling", "Game Physics", "Multiplayer Networking",
    "Photon", "Mirror Networking", "AR", "VR", "Augmented Reality",
    "Virtual Reality", "Game Design", "Level Design", "Animation Programming",

    # Mobile
    "Android", "iOS", "Flutter", "React Native", "Xcode", "Android Studio",

    # Systems / low-level
    "Distributed Systems", "Microservices", "Multithreading", "Concurrency",
    "Operating Systems", "Networking", "Embedded Systems", "Real-Time Systems",

    # Practices / tools
    "Git", "Agile", "Scrum", "Unit Testing", "TDD", "Design Patterns",
    "Data Structures", "Algorithms", "System Design", "OOP",
    "Jira", "Confluence", "Postman",

    # Security
    "Cybersecurity", "OAuth", "JWT", "Encryption", "Penetration Testing",
]

# ---------------------------------------------------------------------------
# CSV column layout
# ---------------------------------------------------------------------------

FINAL_FIELDS = [
    "Job_Title", "Company_Name", "URL", "Location", "Experience", "Salary",
    "Skills_Required", "Matched_Keywords",
]
