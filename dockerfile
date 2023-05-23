# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app files
COPY . .

# Expose port
EXPOSE 3000

# Run the app
CMD [ "python", "app.py" ]
