# Use Python 3.12 base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first (to cache layers)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the full app code
COPY . .

# Run the Flask app
CMD ["python3", "main.py"]
