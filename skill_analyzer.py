import pandas as pd
import psycopg
from category_rules import assign_category
import os

# Connect to PostgreSQL
connection = psycopg.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "job_skill_analyzer"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD")
)
# Get job data from PostgreSQL
query = """
SELECT
    job_id,
    job_title,
    company_name,
    location,
    experience,
    skills_required,
    matched_keywords
FROM jobs;
"""

df = pd.read_sql(query, connection)

print("Jobs loaded from PostgreSQL:", len(df))

# Close the connection
connection.close()

# Split skills for each job
def split_skills(skill_text):
    if pd.isna(skill_text):
        return []

    skills = [skill.strip() for skill in str(skill_text).split(",")]

    # Remove empty values and duplicate skills within the same job
    skills = [skill for skill in skills if skill]

    return list(dict.fromkeys(skills))

# Assign a main category to each job
    # Assign a category to every job
df["category"] = df.apply(assign_category, axis=1)

print("\nJob categories:")
print(df["category"].value_counts())

print("\nSample jobs classified as Other:")
print(df[df["category"] == "Other"]["job_title"].head(30).to_string(index=False))


# Assign a specialization for Software Engineering jobs
def assign_specialization(row):

    if row["category"] != "Software Engineering":
        return ""

    title = str(row["job_title"]).lower()
    skills = str(row["skills_required"]).lower()

    text = title + " " + skills

    # Full Stack
    if any(x in text for x in [
        "full stack",
        "full-stack",
        "fullstack"
    ]):
        return "Full Stack"

    # Backend indicators
    backend_keywords = [
        "backend",
        "back-end",
        "spring",
        "spring boot",
        "node.js",
        "node js",
        "express",
        "django",
        "flask",
        "fastapi",
        "rest api",
        "restful api",
        "microservices",
        "api development",
        "server-side"
    ]

    # Frontend indicators
    frontend_keywords = [
        "frontend",
        "front-end",
        "react",
        "angular",
        "vue",
        "typescript",
        "html",
        "css",
        "ui development",
        "user interface"
    ]

    # Calculate scores
    backend_score = sum(
        1 for keyword in backend_keywords
        if keyword in text
    )

    frontend_score = sum(
        1 for keyword in frontend_keywords
        if keyword in text
    )

    # Decide specialization
    if backend_score > 0 and frontend_score > 0:
        return "Full Stack"

    elif backend_score > frontend_score:
        return "Backend"

    elif frontend_score > backend_score:
        return "Frontend"

    else:
        return "General Software Engineering"

    
# Assign software specialization
df["specialization"] = df.apply(assign_specialization, axis=1)

print("\nSoftware Engineering specializations:")
print(
    df[df["category"] == "Software Engineering"]["specialization"]
    .value_counts()
)


# Apply the function to every job
df["skills_list"] = df["skills_required"].apply(split_skills)

print("\nSkills from first job:")
print(df["skills_list"].iloc[0])

print("\nNumber of unique skills:", len(set(
    skill
    for skill_list in df["skills_list"]
    for skill in skill_list
)))

print("\nSome unique skills:")
print(sorted(set(
    skill
    for skill_list in df["skills_list"]
    for skill in skill_list
))[:50])

# Count how many jobs require each skill
skill_counts = {}

for skill_list in df["skills_list"]:
    for skill in skill_list:
        if skill in skill_counts:
            skill_counts[skill] += 1
        else:
            skill_counts[skill] = 1

# Convert the results into a DataFrame
results = pd.DataFrame(
    list(skill_counts.items()),
    columns=["Skill", "Job_Count"]
)

# Sort from most demanded to least demanded
results = results.sort_values(
    by="Job_Count",
    ascending=False
)

print("\nTop 10 most demanded skills:")
print(results.head(10))

# Calculate skill demand percentage
total_jobs = len(df)

results["Demand_Percentage"] = (
    results["Job_Count"] / total_jobs * 100
).round(2)

# Add ranking
results["Rank"] = range(1, len(results) + 1)

# Arrange the columns
results = results[
    ["Rank", "Skill", "Job_Count", "Demand_Percentage"]
]

print("\nTop 10 skill demand results:")
print(results.head(10))

# Save all skill demand results
results.to_csv(
    "results/skill_demand_results.csv",
    index=False
)

print("\nSkill demand results saved successfully!")


# ---------------------------------------------------------
# Related keyword analysis using Matched_Keywords
# ---------------------------------------------------------

# Choose a skill to analyze
selected_skill = "Python"

related_keyword_counts = {}

# Count how many jobs require the selected skill
skill_job_count = 0

# Go through every job
for _, row in df.iterrows():

    skills = str(row["skills_required"])

    # Check whether the selected skill is required
    if selected_skill.lower() in skills.lower():

        skill_job_count += 1

        # Get matched keywords for this job
        keywords = str(row["matched_keywords"])

        # Split keywords
        keyword_list = [
            keyword.strip()
            for keyword in keywords.split(",")
            if keyword.strip()
        ]

        # Count related keywords
        for keyword in keyword_list:

            # Don't count the selected skill itself
            if keyword.lower() == selected_skill.lower():
                continue

            if keyword in related_keyword_counts:
                related_keyword_counts[keyword] += 1
            else:
                related_keyword_counts[keyword] = 1


# Convert results into a DataFrame
related_results = pd.DataFrame(
    list(related_keyword_counts.items()),
    columns=["Related_Keyword", "Job_Count"]
)

# Calculate percentage among jobs requiring the selected skill
related_results["Demand_Percentage"] = (
    related_results["Job_Count"] / skill_job_count * 100
).round(2)

# Sort from most common to least common
related_results = related_results.sort_values(
    by="Job_Count",
    ascending=False
)

# Add ranking
related_results["Rank"] = range(1, len(related_results) + 1)

# Arrange columns
related_results = related_results[
    ["Rank", "Related_Keyword", "Job_Count", "Demand_Percentage"]
]

print("\nSelected skill:", selected_skill)
print("Jobs requiring", selected_skill + ":", skill_job_count)

print("\nKeywords commonly required alongside", selected_skill + ":")
print(related_results.head(10))


# Save related keyword results
related_results.to_csv(
    "results/related_keywords.csv",
    index=False
)

print("\nRelated keyword results saved successfully!")
