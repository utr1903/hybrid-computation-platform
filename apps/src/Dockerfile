# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Get the app name from the build args
ARG APP_NAME

# Create a directory for the application
RUN mkdir app

# Copy the requirements file into the container app directory
COPY ./${APP_NAME}/requirements.txt ./app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r ./app/requirements.txt

# Copy the commons directory into the container
COPY ./commons ./commons

# Copy the application code into the container at /app
COPY ./${APP_NAME} ./app

# Set environment variables for production
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app/main.py"]
