# Job Skill Demand Analyzer

## Project Overview

The Job Skill Demand Analyzer is a Python-based web application that analyzes job listings to identify in-demand skills and explore job market trends.

The project collects job listing data, cleans and processes it, stores it in PostgreSQL, performs skill demand analysis, and presents the results through an interactive Django dashboard.

## Features

- Job data cleaning and preprocessing
- PostgreSQL database storage
- Skill demand analysis
- Job category classification
- Filtering by category, location, experience, and company
- Interactive Plotly skill-demand chart
- Skill demand table
- Clickable skill details
- Tools and technologies associated with a selected skill
- Job categories, locations, experience levels, and companies
- Matching job listings with original job links

## Technology Stack

- Python
- Pandas
- NumPy
- PostgreSQL
- Psycopg
- Django
- Plotly
- Requests
- BeautifulSoup
- Selenium

## Dataset

The current dataset contains 657 job listings.

## Project Flow

Job Data  
↓  
Data Cleaning  
↓  
PostgreSQL  
↓  
Skill Demand Analysis  
↓  
Django Dashboard  
↓  
Filters and Plotly Visualization  
↓  
Skill Details

## Running the Project

### Install dependencies

```bash
pip install -r requirements.txt

```markdown
### Set up PostgreSQL

Create a PostgreSQL database named:

```text
job_skill_analyzer

### Run database setup

After PostgreSQL is running, execute:

```bash
python manage.py migrate

### Run the web application

Start the Django development server:

```bash
python manage.py runserver
