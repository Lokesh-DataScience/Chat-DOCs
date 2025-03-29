# Use Python 3.11-slim base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install dependencies in a single RUN command for efficiency
RUN apt-get update && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the app
EXPOSE 5000

# Use Waitress to serve the Flask app
CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "5000", "app:app"]
