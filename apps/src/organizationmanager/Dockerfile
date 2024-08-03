# Use an official Python runtime as a parent image
FROM python:3.11-slim

ARG APP_NAME

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Set environment variables for production
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port 8080 for the Flask app
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
