# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Install the PostgreSQL client and development libraries
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set a non-root user
RUN useradd -m appuser
USER appuser

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY --chown=appuser:appuser requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY --chown=appuser:appuser . .

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
CMD ["python", "app.py"]
