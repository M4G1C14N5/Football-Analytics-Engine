# Use the official Selenium image which includes Chrome and ChromeDriver
FROM selenium/standalone-chrome:latest

# Switch to root to perform system updates and installations
USER root

# Install Python and Pip without manual linking to avoid Debian system conflicts
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory for all subsequent commands
WORKDIR /app

# Create the data directory and ensure permissions for the 'seluser'
RUN mkdir -p data_html && chown -R seluser:seluser /app

# Switch back to the standard Selenium user for security
USER seluser

# Copy and install Python dependencies using the break-system-packages flag
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Start the script (main.py will be mounted via volumes in docker-compose)
# The selenium/standalone-chrome image starts the selenium server automatically via entrypoint
# We just need to ensure it's running before our Python script starts
CMD ["python3", "main.py"]