# Use an official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for TA-Lib
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libatlas-base-dev \
    libta-lib0 \
    libta-lib-dev && \
    pip install ta-lib

# Copy application files to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Start the Flask server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
