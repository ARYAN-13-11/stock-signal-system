# Use Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libatlas-base-dev \
    wget \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy all files to container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Copy Supervisor config file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start Supervisor (which will start both app.py and data_fetch.py)
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
