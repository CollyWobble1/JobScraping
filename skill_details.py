import os

import pandas as pd
import psycopg

from category_rules import assign_category


def split_skills(skill_text):
    if pd.isna(skill_text):
        return []

    skills = [
        skill.strip()
        for skill in str(skill_text).split(",")
        if skill.strip()
    ]

    return list(dict.fromkeys(skills))


def get_skill_details(selected_skill):

    connection = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "job_skill_analyzer"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )

    query = """
    SELECT
        job_id,
        job_title,
        company_name,
        location,
        experience,
        url,
        skills_required,
        matched_keywords
    FROM jobs;
    """

    df = pd.read_sql(query, connection)

    print("Jobs loaded from PostgreSQL:", len(df))

    connection.close()

    print("\nSelected skill:", selected_skill)

    df["skills_list"] = df["skills_required"].apply(split_skills)

    matching_jobs = df[
        df["skills_list"].apply(
            lambda skills: any(
                skill == selected_skill
                for skill in skills
            )
        )
    ].copy()

    print(
        "Jobs requiring",
        selected_skill + ":",
        len(matching_jobs)
    )

    total_jobs = len(df)
    skill_job_count = len(matching_jobs)

    if total_jobs > 0:
        demand_percentage = (
            skill_job_count / total_jobs * 100
        )
    else:
        demand_percentage = 0

    print(
        "Demand percentage:",
        round(demand_percentage, 2),
        "%"
    )

    related_keyword_counts = {}

    for _, row in matching_jobs.iterrows():

        keywords = str(row["matched_keywords"])

        keyword_list = [
            keyword.strip()
            for keyword in keywords.split(",")
            if keyword.strip()
        ]

        for keyword in keyword_list:

            if keyword.lower() == selected_skill.lower():
                continue

            if keyword in related_keyword_counts:
                related_keyword_counts[keyword] += 1
            else:
                related_keyword_counts[keyword] = 1

    related_results = pd.DataFrame(
        list(related_keyword_counts.items()),
        columns=["Related_Keyword", "Job_Count"]
    )

    if skill_job_count > 0 and len(related_results) > 0:

        related_results["Demand_Percentage"] = (
            related_results["Job_Count"]
            / skill_job_count
            * 100
        ).round(2)

        related_results = related_results.sort_values(
            by="Job_Count",
            ascending=False
        )

    print(
        "\nKeywords commonly required alongside",
        selected_skill + ":"
    )

    print(related_results.head(10))

    matching_jobs["category"] = matching_jobs.apply(
        assign_category,
        axis=1
    )

    category_counts = (
        matching_jobs["category"]
        .value_counts()
    )

    print(
        "\nCategories where",
        selected_skill,
        "is demanded:"
    )

    print(category_counts)

    location_counts = (
        matching_jobs["location"]
        .value_counts()
    )

    print(
        "\nLocations where",
        selected_skill,
        "is demanded:"
    )

    print(location_counts.head(10))

    experience_counts = (
        matching_jobs["experience"]
        .value_counts()
    )

    print(
        "\nExperience levels where",
        selected_skill,
        "is demanded:"
    )

    print(experience_counts)

    company_counts = (
        matching_jobs["company_name"]
        .value_counts()
    )

    print(
        "\nCompanies hiring for",
        selected_skill + ":"
    )

    print(company_counts.head(10))

    print(
        "\nJobs requiring",
        selected_skill + ":"
    )

    job_listings = matching_jobs[
        [
            "job_title",
            "company_name",
            "location",
            "experience",
            "url"
        ]
    ].head(10)

    print(job_listings)

    return {
        "matching_jobs": matching_jobs,
        "demand_percentage": demand_percentage,
        "related_keywords": related_results,
        "categories": category_counts,
        "locations": location_counts,
        "experience": experience_counts,
        "companies": company_counts,
        "job_listings": job_listings
    }
