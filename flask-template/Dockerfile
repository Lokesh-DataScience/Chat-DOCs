# Use Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the source code
COPY . .

# Set environment variable for Google Credentials
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/chat-docs-credentials.json"

# Start the server
CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "5000", "app:app"]
