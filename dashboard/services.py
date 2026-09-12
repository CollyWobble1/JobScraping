import csv
from collections import Counter
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "jobs_cleaned.csv"


def split_values(value):
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def load_jobs():
    with DATA_FILE.open(newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def category_for(title):
    title = title.lower()
    rules = {
        "Data Science": ("data scientist", "data science"),
        "Data Engineering": ("data engineer", "data engineering"),
        "Data Analytics": ("data analyst", "data analytics", "business analyst"),
        "Cybersecurity": ("cybersecurity", "cyber security", "security engineer", "security analyst"),
        "Cloud/DevOps": ("devops", "site reliability", "sre", "cloud engineer", "cloud architect"),
        "QA/Testing": ("qa engineer", "quality assurance", "test engineer", "software tester"),
        "Networking": ("network engineer", "network administrator"),
        "Hardware/Embedded": ("embedded", "firmware", "hardware engineer"),
        "Management": ("manager", "director", "vice president", "head of"),
        "Design/UX": ("ux", "ui designer", "user experience", "product designer"),
        "IT Operations/Support": ("administrator", "technical support", "it support", "help desk"),
        "Software Engineering": ("software engineer", "software developer", "developer", "programmer", "technical lead"),
    }
    for category, terms in rules.items():
        if any(term in title for term in terms):
            return category
    return "Other"


def enrich(rows):
    for index, row in enumerate(rows, start=1):
        row["id"] = str(index)
        row["category"] = category_for(row.get("Job_Title", ""))
    return rows


def filter_jobs(rows, params):
    category = params.get("category", "All")
    location = params.get("location", "All")
    experience = params.get("experience", "All")
    company = params.get("company", "").strip().lower()

    return [
        row for row in rows
        if (category == "All" or row["category"] == category)
        and (location == "All" or location.lower() in row["Location"].lower())
        and (experience == "All" or experience.lower() in row["Experience"].lower())
        and (not company or company in row["Company_Name"].lower())
    ]


def skill_demand(rows):
    counts = Counter()
    for row in rows:
        counts.update(set(split_values(row.get("Skills_Required"))))
    total = len(rows)
    return [
        {
            "skill": skill,
            "count": count,
            "percentage": round(count / total * 100, 2) if total else 0,
        }
        for skill, count in counts.most_common()
    ]


def distribution(rows, field):
    return [{"label": label, "count": count} for label, count in Counter(row[field] for row in rows).most_common(8)]


def chart_json(items, label_key):
    return {"labels": [item[label_key] for item in items], "values": [item["count"] for item in items]}