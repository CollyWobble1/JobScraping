import os
import getpass
import pandas as pd
import psycopg


# Load cleaned data
df = pd.read_csv("data/jobs_cleaned.csv")

print("Jobs loaded from CSV:", len(df))


# Database configuration
connection = psycopg.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "job_skill_analyzer"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD") or getpass.getpass("PostgreSQL password: ")
)

cursor = connection.cursor()


# Create table
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


# Make URL unique so the same job cannot be inserted twice
cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS jobs_url_unique
    ON jobs(url)
""")


# Insert new jobs or update existing jobs
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

        ON CONFLICT (url)
        DO UPDATE SET
            job_title = EXCLUDED.job_title,
            company_name = EXCLUDED.company_name,
            location = EXCLUDED.location,
            experience = EXCLUDED.experience,
            salary = EXCLUDED.salary,
            skills_required = EXCLUDED.skills_required,
            matched_keywords = EXCLUDED.matched_keywords
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


connection.commit()

print("Database updated successfully!")

cursor.close()
connection.close()

print("Database connection closed.")
