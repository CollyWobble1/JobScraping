import json

import pandas as pd
import plotly.express as px
from django.db import connection
from django.shortcuts import render
from plotly.utils import PlotlyJSONEncoder

from filter_analysis import filter_jobs
from skill_details import get_skill_details


CATEGORIES = [
    "All",
    "Software Engineering",
    "Data Science",
    "Data Engineering",
    "Data Analytics",
    "Cloud/DevOps",
    "Cybersecurity",
    "QA/Testing",
    "Networking",
    "Hardware/Embedded",
    "Systems/Infrastructure",
    "Architecture/Consulting",
    "Management",
    "Sales/Business",
    "Business/Compliance",
    "Design/UX",
    "IT Operations/Support",
    "HR/Recruitment",
    "Engineering/Industrial",
    "Other",
]


def get_filter_options():
    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT DISTINCT location
            FROM jobs
            WHERE location IS NOT NULL
              AND location <> ''
            ORDER BY location;
        """)

        locations = [
            row[0]
            for row in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT DISTINCT experience
            FROM jobs
            WHERE experience IS NOT NULL
              AND experience <> ''
            ORDER BY experience;
        """)

        experiences = [
            row[0]
            for row in cursor.fetchall()
        ]

    return locations, experiences


def home(request):

    selected_category = request.GET.get(
        "category",
        "All"
    )

    selected_location = request.GET.get(
        "location",
        "All"
    )

    selected_experience = request.GET.get(
        "experience",
        "All"
    )

    company_search = request.GET.get(
        "company",
        ""
    ).strip()

    filtered_jobs, skill_results = filter_jobs(
        selected_category,
        selected_location,
        selected_experience,
        company_search
    )

    top_skills = skill_results.head(10)

    if len(top_skills) > 0:

        fig = px.bar(
            top_skills,
            x="Demand_Percentage",
            y="Skill",
            orientation="h",
            title="Top 10 Skills in Demand",
            labels={
                "Demand_Percentage": "Demand (%)",
                "Skill": "Skill"
            }
        )

        fig.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            },
            height=500
        )

        chart_json = json.dumps(
            fig,
            cls=PlotlyJSONEncoder
        )

    else:

        chart_json = json.dumps({
            "data": [],
            "layout": {
                "title": "No matching jobs"
            }
        })

    locations, experiences = get_filter_options()

    return render(
        request,
        "dashboard/home.html",
        {
            "chart_json": chart_json,
            "top_skills": top_skills.to_dict("records"),

            "categories": CATEGORIES,
            "locations": locations,
            "experiences": experiences,

            "selected_category": selected_category,
            "selected_location": selected_location,
            "selected_experience": selected_experience,
            "company_search": company_search,

            "job_count": len(filtered_jobs),
        }
    )


def skill_detail(request):

    selected_skill = request.GET.get(
        "skill",
        ""
    ).strip()

    if not selected_skill:

        return render(
            request,
            "dashboard/skill_details.html",
            {
                "selected_skill": "No skill selected",
                "job_count": 0,
                "demand_percentage": 0,
                "related_keywords": [],
                "categories": [],
                "locations": [],
                "experience": [],
                "companies": [],
                "jobs": [],
            }
        )

    details = get_skill_details(
        selected_skill
    )

    related_keywords = (
        details["related_keywords"]
        .head(10)
        .to_dict("records")
    )

    categories = [
        {
            "category": category,
            "count": count
        }
        for category, count
        in details["categories"].items()
    ]

    locations = [
        {
            "location": location,
            "count": count
        }
        for location, count
        in details["locations"].head(10).items()
    ]

    experience = [
        {
            "experience": exp,
            "count": count
        }
        for exp, count
        in details["experience"].items()
    ]

    companies = [
        {
            "company": company,
            "count": count
        }
        for company, count
        in details["companies"].head(10).items()
    ]

    jobs = details["job_listings"].to_dict(
        "records"
    )

    return render(
        request,
        "dashboard/skill_details.html",
        {
            "selected_skill": selected_skill,
            "job_count": len(
                details["matching_jobs"]
            ),
            "demand_percentage": round(
                details["demand_percentage"],
                2
            ),
            "related_keywords": related_keywords,
            "categories": categories,
            "locations": locations,
            "experience": experience,
            "companies": companies,
            "jobs": jobs,
        }
    )
