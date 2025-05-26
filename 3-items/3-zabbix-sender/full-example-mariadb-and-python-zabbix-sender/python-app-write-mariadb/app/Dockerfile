# Use the official Python image from the Docker Hub
FROM hub.hamdocker.ir/python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Command to run the application
CMD ["python", "app.py"]