# Skill Atlas

Django dashboard for exploring the job-skill analysis dataset.

## Run locally

```powershell
.\venv\Scripts\activate
python manage.py check
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

The dashboard currently reads `data/jobs_cleaned.csv`, which keeps local development independent of PostgreSQL. It includes an overview, filtered job explorer, and skill profile view. The original scraping and analysis scripts remain available at the project root.
