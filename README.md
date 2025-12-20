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

### Phase 2: The Cloudflare "Renegade" Pivot

#### The Problem

Local network port-forwarding issues made ZeroTier or standard Nginx setups difficult for a public-facing site.

#### The Solution

Switched to a **Cloudflare Tunnel (Cloudflared)**, which creates a secure, outbound "wormhole" from the server to Cloudflare's edge.

#### Cloudflare Setup

1. **Tunnel Creation**: Created the `FAE_tunnel` in the Cloudflare Zero Trust dashboard
2. **Connector**: Successfully ran a Connector on the server to link it to the tunnel
3. **Published Application Route**: Configured a Published Application Route (modern version of a Public Hostname) to map `fae.camuedlabs.org` directly to the dashboard container on port 8501
4. **DNS Optimization**: No need to manually create A records or expose home IP address; Cloudflare handles DNS routing automatically through the tunnel

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
- **ETL**: Python (pandas, SQLAlchemy, BeautifulSoup4)
- **Dashboard**: Streamlit
- **Reverse Proxy**: Nginx
- **Tunneling**: Cloudflare Tunnel (Cloudflared)
- **Domain**: fae.camuedlabs.org

## Getting Started

1. Clone the repository
2. Set up your `.env` file with necessary secrets (DB passwords, API keys)
3. Configure Cloudflare Tunnel (if deploying publicly)
4. Run `docker-compose up` to start all services

## Deployment

The project is designed to be deployed on an Ubuntu server with:
- Docker and Docker Compose installed
- Cloudflare Tunnel connector configured
- DNS configured through Cloudflare Zero Trust dashboard

---

*FAE - Providing actionable football insights through data analytics and predictive modeling.*

