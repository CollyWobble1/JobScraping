import pandas as pd
import psycopg

# Load cleaned data
df = pd.read_csv("data/jobs_cleaned.csv")

print("Jobs loaded from CSV:", len(df))

# Connect to PostgreSQL
connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="job_skill_analyzer",
    user="postgres",
    password="your_password"
)

cursor = connection.cursor()

# Create jobs table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id SERIAL PRIMARY KEY,
        job_title TEXT,
        company_name TEXT,
        url TEXT,
        location TEXT,
        experience TEXT,
        salary TEXT,
        skills_required TEXT,
        matched_keywords TEXT
    )
""")

# Insert jobs
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO jobs (
            job_title,
            company_name,
            url,
            location,
            experience,
            salary,
            skills_required,
            matched_keywords
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row["Job_Title"],
        row["Company_Name"],
        row["URL"],
        row["Location"],
        row["Experience"],
        row["Salary"],
        row["Skills_Required"],
        row["Matched_Keywords"]
    ))

# Save changes
connection.commit()

print("Jobs inserted into PostgreSQL successfully!")

# Close connection
cursor.close()
connection.close()

print("Database connection closed.")