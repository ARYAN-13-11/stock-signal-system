# Use Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all files to container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Start both Flask API & Data Fetcher
CMD ["sh", "-c", "python data_fetch.py & python app.py"]
