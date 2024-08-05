# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Copy the commons directory into the container
COPY ./commons ./commons

# Get the app name from the build args
ARG APP_NAME

# Set the working directory in the container
WORKDIR /app

COPY ./${APP_NAME} .

# Copy the requirements file into the container app directory
COPY ./${APP_NAME}/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY ./${APP_NAME} .

# Set environment variables for production
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]
