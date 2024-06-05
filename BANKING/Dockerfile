# Use the official Python image as a base image
FROM python:3.11.4-slim-buster

# Set environment variables for Python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set work directory
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port
EXPOSE 8000

# Run Django development server
CMD ["python", "manage.py", "runserver", "dockerhost:8000"]
