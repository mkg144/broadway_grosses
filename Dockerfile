# Use an official Python runtime as the base image
FROM python:3.9.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container's working directory
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set the default environment variables (if needed)
# Example: ENV ENV_VARIABLE_NAME=value
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gcp_secret_key.json

# Install Jupyter Notebook
RUN pip install --no-cache-dir jupyter

# Expose the Jupyter Notebook port
EXPOSE 8888

# Run your script.py when the container starts
# CMD ["python", "main.py"]
