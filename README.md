# Football Analytics Engine (FAE)

FAE (pronounced 'Fae') is Fotmob's renegade cousin. Keep up with your favorite teams, players, and leagues. The goal of FAE is to provide actionable insight that Football analysts, recruiters or enthusiasts can use.

## Overview

FAE is a comprehensive football analytics platform designed to deliver actionable insights through data organization, analysis, and predictive modeling. The system is built with a modular architecture that enables scalable data processing and visualization.

## Features

FAE provides the following capabilities:

- **Data Organization**: Allow users to organize data by various features (similar to SQL operations)
- **Insights & Metrics**: Provide insights and relevant sports metrics
- **Predictive Models**: Use models that could possibly predict:
  - Team of the Year (TOTY)
  - Overall best performing player
  - Best performing squads

## Project Architecture

### Phase 1: Project Architecture

The project is designed to be deployed from an Ubuntu server with DNS configuration. The architecture uses Docker for containerization, providing better encapsulation and modularity.

#### Initial Design Evolution

**Original Concept**: Hard-coded logical steps with containers running continuously
- Container for Python scripts that scrape websites (Extract)
- Container for the loading phase using SQL
- Container for Transformation and prediction

**Optimized Approach**: Services running continuously with on-demand job execution
- **Services** (running continuously):
  - Database (PostgreSQL)
  - Dashboard (Streamlit UI)
  - Gateway (Nginx)
- **Jobs** (executed on-demand):
  - Python runner (ETL job)

This approach is more efficient and less costly, as containers don't need to run all the time waiting to pass off results.

### Infrastructure

- **Modular Directory Structure**: Initialized with `etl_job/` (for data processing), `dashboard/` (for the Streamlit UI), and root directory for orchestration
- **Containerization**: Dockerfiles package Python environments, ensuring consistent execution across development and production (Pavilion laptop → Ubuntu server)
- **Orchestration**: `docker-compose.yml` acts as the "director," linking Postgres database, ETL worker, Dashboard, and Tunnel connector into a single private network
- **Security (Local)**: `.gitignore` and `.env` pattern ensure database passwords and API tokens never get leaked to GitHub

### MLOps & DevOps Practices

The goal is to involve MLOps best practices throughout the entire project, incorporating principles from both Data Engineering and DevOps:

- **Docker, the Architect**: Designed the core behavior of this project, providing containerization and consistent environments across development and production
- **Apache Airflow, the Conductor**: DAGs (Directed Acyclic Graphs) are used to manage the ETL pipeline, triggering jobs as requested, and handling job failures and retries automatically
- **CI/CD Pipeline**: 
  - Development is done on the local laptop
  - Git/GitHub provides version control
  - Testing is automated using GX Core (Great Expectations) for data quality validation
  - Deployment done in Ubuntu Server

### Phase 2: The Cloudflare "Renegade" Pivot

#### The Problem

Local network port-forwarding issues made ZeroTier or standard Nginx setups difficult for a public-facing site.

#### The Solution

Switched to a **Cloudflare Tunnel (Cloudflared)**, which creates a secure, outbound "wormhole" from the server to Cloudflare's edge. Configured and published application route (`fae.camuedlabs.org`). Nginx is no longer needed since cloudfare alse takes care of reverse proxy.

### Phase 3: ETL Pipeline Development (Current)

Currently in the phase of adding and debugging the scraping script. The ETL pipeline follows a multi-stage data extraction and processing workflow:

#### Scraping Logic Flow

graph LR
    A[Chromium Driver] -- "Access fbref.com" --> B(Raw HTML)
    B -- "Save Snapshot" --> C[data_html/*.txt]
    C -- "BeautifulSoup Parsing" --> D{Pandas DataFrame}
    D -- "Structured Export" --> E[uncleaned_data_csv/*.csv]
    E -- "Orchestration" --> F((Airflow DAG))

**Current Challenges:**
- Cloudflare bot detection requiring Selenium instead of simple HTTP requests
- Handling multiple seasons and data types (squad stats, player stats, wages, etc.)
- Ensuring robust error handling and retry logic for web scraping operations

**Solution**
- Selenium & Chromium: utilizes a headless Chromium Driver within the Docker environment to simulate real user interactions, bypassing anti-bot measures like Cloudflare challenges.
- Docker Optimization: The Chrome environment and necessary drivers are baked directly into the etl_job Dockerfile to ensure a consistent, "plug-and-play" scraping environment.

## File Structure

```
football-analytics-project/
├── docker-compose.yml         # The "Master Architect" file
├── .env                       # Stores secrets (DB passwords, API keys)
├── .gitignore                 # Ensures secrets don't get committed
├── nginx/
│   └── nginx.conf             # Config to connect your Domain to the App
├── postgres_data/             # (Created automatically) Persistent DB storage
├── etl_job/                   # THE RUNNER
│   ├── Dockerfile             # Instructions to build the Python environment
│   ├── requirements.txt       # pandas, sqlalchemy, beautifulsoup4, etc.
│   ├── main.py                # The entry point (scheduler)
│   ├── scripts/
│   │   ├── extract.py         # Scraping logic
│   │   ├── load.py            # SQL push logic
│   │   └── transform.py       # ML models & TOTY logic
│   └── utils.py               # Helper functions (DB connections)
└── dashboard/                 # THE UI
    ├── Dockerfile             # Instructions for Streamlit environment
    ├── requirements.txt       # streamlit, plotly, etc.
    └── app.py                 # The Streamlit dashboard code
```

*Note: File structure is subject to change*

## Technology Stack

- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL
- **Workflow Orchestration**: Apache Airflow (DAG-based ETL pipeline management)
- **ETL**: Python (pandas, SQLAlchemy, BeautifulSoup4)
- **Dashboard**: Streamlit
- **Data Quality**: GX Core (Great Expectations) for automated testing
- **Version Control**: Git/GitHub
- **CI/CD**: Automated testing and deployment pipeline
- **Tunneling**: Cloudflare Tunnel (Cloudflared)
- **Domain**: fae.camuedlabs.org

## Getting Started

1. Clone the repository
2. Set up your `.env` file with necessary secrets (DB passwords, API keys)
3. Configure Cloudflare Tunnel (if deploying publicly)
4. Run `docker-compose up` to start all services

---

*FAE - Providing actionable football insights through data analytics and predictive modeling.*

