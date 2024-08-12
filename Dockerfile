# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the kaggle.json (for API credentials)
COPY kaggle.json /root/.kaggle/kaggle.json

# Set permissions on kaggle.json
RUN chmod 600 /root/.kaggle/kaggle.json

