# Use a base image for Python
FROM python:3.11.9-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install dependencies required for OpenCV
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*
    
# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Command to run on container start
CMD ["python", "app.py"]
