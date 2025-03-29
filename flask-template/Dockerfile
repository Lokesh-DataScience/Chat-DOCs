# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 5000

# Use waitress for WSGI compatibility
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]
