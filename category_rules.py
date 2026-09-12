# Category classification rules


def assign_category(row):

    title = str(row["job_title"]).lower()
    skills = str(row["skills_required"]).lower()

    # We mainly use the job title for the main category.
    # Skills are used only where needed.

    # ----- DATA -----

    if any(x in title for x in [
        "data scientist",
        "data science"
    ]):
        return "Data Science"

    elif any(x in title for x in [
        "data engineer",
        "data engineering"
    ]):
        return "Data Engineering"

    elif any(x in title for x in [
        "data analyst",
        "data analytics",
        "business analyst"
    ]):
        return "Data Analytics"


    # ----- CYBERSECURITY -----

    elif any(x in title for x in [
        "cybersecurity",
        "cyber security",
        "information security",
        "security engineer",
        "security analyst"
    ]):
        return "Cybersecurity"


    # ----- CLOUD / DEVOPS -----

    elif any(x in title for x in [
        "devops",
        "site reliability",
        "sre",
        "cloud engineer",
        "cloud architect",
        "cloud computing"
    ]):
        return "Cloud/DevOps"


    # ----- QA / TESTING -----

    elif any(x in title for x in [
        "qa engineer",
        "quality assurance",
        "test engineer",
        "software tester",
        "testing engineer"
    ]):
        return "QA/Testing"


    # ----- NETWORKING -----

    elif any(x in title for x in [
        "network engineer",
        "networking engineer",
        "network administrator"
    ]):
        return "Networking"


    # ----- HARDWARE / EMBEDDED -----

    elif any(x in title for x in [
        "embedded",
        "firmware",
        "hardware engineer",
        "electronics engineer"
    ]):
        return "Hardware/Embedded"


    # ----- SYSTEMS / INFRASTRUCTURE -----

    elif any(x in title for x in [
        "system engineer",
        "systems engineer",
        "infrastructure engineer",
        "platform engineer",
        "linux engineer"
    ]):
        return "Systems/Infrastructure"


    # ----- ARCHITECTURE / CONSULTING -----

    elif any(x in title for x in [
        "architect",
        "consultant",
        "consulting"
    ]):
        return "Architecture/Consulting"


    # ----- MANAGEMENT -----

    elif any(x in title for x in [
        "manager",
        "director",
        "vice president",
        " vp ",
        "head of"
    ]):
        return "Management"


    # ----- HR -----

    elif any(x in title for x in [
        "hr ",
        "human resource",
        "recruiter",
        "recruitment"
    ]):
        return "HR/Recruitment"


    # ----- SALES / BUSINESS -----

    elif any(x in title for x in [
        "sales",
        "business development",
        "account manager",
        "customer success"
    ]):
        return "Sales/Business"


    # ----- BUSINESS / COMPLIANCE -----

    elif any(x in title for x in [
        "compliance",
        "legal",
        "risk analyst"
    ]):
        return "Business/Compliance"


    # ----- DESIGN -----

    elif any(x in title for x in [
        "ux",
        "ui designer",
        "user experience",
        "product designer"
    ]):
        return "Design/UX"


    # ----- INDUSTRIAL ENGINEERING -----

    elif any(x in title for x in [
        "civil engineer",
        "mechanical engineer",
        "electrical engineer",
        "industrial engineer",
        "automotive engineer",
        "manufacturing engineer",
        "diesel mechanic",
        "petrol mechanic",
        "handyman",
        "bowling technician"
    ]):
        return "Engineering/Industrial"


    # ----- IT OPERATIONS / SUPPORT -----

    elif any(x in title for x in [
        "administrator",
        "technical support",
        "it support",
        "help desk",
        "support engineer"
    ]):
        return "IT Operations/Support"


    # ----- SOFTWARE ENGINEERING -----

    elif any(x in title for x in [
        "software engineer",
        "software developer",
        "software development",
        "application developer",
        "programmer",
        "developer",
        "computer scientist",
        "research scientist",
        "product engineer",
        "technical lead",
        "technical specialist",
        "systems development engineer",
        "customer engineer"
    ]):
        return "Software Engineering"


    # ----- OTHER -----

    else:
        return "Other"