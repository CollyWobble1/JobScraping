from django.shortcuts import render

from .services import chart_json, distribution, enrich, filter_jobs, load_jobs, skill_demand


def common_context(rows, request):
    categories = sorted({row["category"] for row in rows})
    locations = sorted({row["Location"] for row in rows if row["Location"]})
    experiences = sorted({row["Experience"] for row in rows if row["Experience"]})
    return {
        "categories": categories,
        "locations": locations,
        "experiences": experiences,
        "selected_category": request.GET.get("category", "All"),
        "selected_location": request.GET.get("location", "All"),
        "selected_experience": request.GET.get("experience", "All"),
        "company_query": request.GET.get("company", ""),
    }


def dashboard(request):
    rows = enrich(load_jobs())
    filtered = filter_jobs(rows, request.GET)
    skills = skill_demand(filtered)
    categories = distribution(filtered, "category")
    locations = distribution(filtered, "Location")
    experiences = distribution(filtered, "Experience")
    context = {
        **common_context(rows, request),
        "total_jobs": len(filtered),
        "total_skills": len(skills),
        "top_skill": skills[0] if skills else {"skill": "No data", "count": 0},
        "skills": skills[:10],
        "categories_chart": chart_json(categories, "label"),
        "locations_chart": chart_json(locations, "label"),
        "experiences_chart": chart_json(experiences, "label"),
        "active_filters": any(request.GET.get(key) for key in ("category", "location", "experience", "company")),
    }
    return render(request, "dashboard/home.html", context)


def jobs(request):
    rows = enrich(load_jobs())
    filtered = filter_jobs(rows, request.GET)
    context = {
        **common_context(rows, request),
        "jobs": filtered,
        "job_count": len(filtered),
    }
    return render(request, "dashboard/jobs.html", context)


def skill_detail(request):
    rows = enrich(load_jobs())
    selected = request.GET.get("name", "Software Development")
    matching = [row for row in rows if selected.lower() in row["Skills_Required"].lower()]
    related = skill_demand(matching)
    context = {
        **common_context(rows, request),
        "selected_skill": selected,
        "matching_count": len(matching),
        "demand_percentage": round(len(matching) / len(rows) * 100, 2) if rows else 0,
        "related_skills": [item for item in related if item["skill"].lower() != selected.lower()][:8],
        "category_chart": chart_json(distribution(matching, "category"), "label"),
        "location_chart": chart_json(distribution(matching, "Location"), "label"),
        "matching_jobs": matching[:12],
    }
    return render(request, "dashboard/skill_detail.html", context)