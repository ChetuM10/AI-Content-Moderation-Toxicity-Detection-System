# Use Python 3.10 image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Set environment variables
ENV FLASK_APP=app.py
ENV PORT=7860

# Run the application
CMD ["python", "app.py"]
