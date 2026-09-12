import pandas as pd
import psycopg
from category_rules import assign_category


def filter_jobs(selected_category, selected_location, selected_experience, company_search):

    # Connect to PostgreSQL
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="job_skill_analyzer",
        user="postgres",
        password="9987733381k"
    )

    # Get job data from PostgreSQL
    query = """
    SELECT
        job_id,
        job_title,
        company_name,
        url,
        location,
        experience,
        skills_required,
        matched_keywords
    FROM jobs;
    """

    df = pd.read_sql(query, connection)

    print("Jobs loaded from PostgreSQL:", len(df))

    # Assign categories
    df["category"] = df.apply(assign_category, axis=1)

    # ---------------------------------------------------------
    # Category filter
    # ---------------------------------------------------------

    if selected_category == "All":
        filtered_df = df.copy()
    else:
        filtered_df = df[
            df["category"] == selected_category
        ].copy()

    print("\nSelected category:", selected_category)
    print("Jobs after category filter:", len(filtered_df))

    # ---------------------------------------------------------
    # Location filter
    # ---------------------------------------------------------

    if selected_location == "All":
        filtered_df = filtered_df.copy()
    else:
        filtered_df = filtered_df[
            filtered_df["location"].str.contains(
                selected_location,
                case=False,
                na=False
            )
        ].copy()

    print("\nSelected location:", selected_location)
    print("Jobs after location filter:", len(filtered_df))

    # ---------------------------------------------------------
    # Experience filter
    # ---------------------------------------------------------

    if selected_experience == "All":
        filtered_df = filtered_df.copy()
    else:
        filtered_df = filtered_df[
            filtered_df["experience"].str.contains(
                selected_experience,
                case=False,
                na=False
            )
        ].copy()

    print("\nSelected experience:", selected_experience)
    print("Jobs after experience filter:", len(filtered_df))

    # ---------------------------------------------------------
    # Company search
    # ---------------------------------------------------------

    if company_search == "":
        filtered_df = filtered_df.copy()
    else:
        filtered_df = filtered_df[
            filtered_df["company_name"].str.contains(
                company_search,
                case=False,
                na=False
            )
        ].copy()

    print(
        "\nCompany search:",
        company_search if company_search else "All"
    )
    print(
        "Jobs after company search:",
        len(filtered_df)
    )

    # ---------------------------------------------------------
    # Skill demand for filtered jobs
    # ---------------------------------------------------------

    skill_counts = {}

    for skill_list in filtered_df["skills_required"]:

        skills = [
            skill.strip()
            for skill in str(skill_list).split(",")
            if skill.strip()
        ]

        skills = list(dict.fromkeys(skills))

        for skill in skills:

            if skill in skill_counts:
                skill_counts[skill] += 1
            else:
                skill_counts[skill] = 1

    filtered_skill_results = pd.DataFrame(
        list(skill_counts.items()),
        columns=["Skill", "Job_Count"]
    )

    if len(filtered_df) > 0:

        filtered_skill_results["Demand_Percentage"] = (
            filtered_skill_results["Job_Count"]
            / len(filtered_df)
            * 100
        ).round(2)

        filtered_skill_results = filtered_skill_results.sort_values(
            by="Job_Count",
            ascending=False
        )

        filtered_skill_results["Rank"] = range(
            1,
            len(filtered_skill_results) + 1
        )

        filtered_skill_results = filtered_skill_results[
            [
                "Rank",
                "Skill",
                "Job_Count",
                "Demand_Percentage"
            ]
        ]

        print("\nTop 10 skills after filters:")
        print(filtered_skill_results.head(10))

    else:

        print("\nNo jobs match the selected filters.")

    connection.close()

    return filtered_df, filtered_skill_results

