# Use a lightweight Python base image
FROM python:3.9-slim

# Install system dependencies required for postgres and scraping
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Create the directory for your CSV outputs
RUN mkdir -p uncleaned_data_csv

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your scraper code
COPY . .

# Set the default command to run your main script
CMD ["python", "main.py"]
