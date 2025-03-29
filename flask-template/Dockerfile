# Use official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the app code
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Run the Gunicorn server with WSGI
CMD ["uvicorn", "app:asgi_app", "--host", "0.0.0.0", "--port", "5000"]
