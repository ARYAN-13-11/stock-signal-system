# Use Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy all files to container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Start Flask server
CMD ["python", "app.py"]
