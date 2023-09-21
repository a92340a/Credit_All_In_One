# Use an official Python runtime as a parent image
FROM python:3.9.18-slim

# Create a working directory in the container
WORKDIR /server_producer

# Copy the current directory contents into the container at /server_producer
COPY . /server_producer

# Install any needed packages specified in requirements.txt
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r requirements.txt

# Define command to run app
EXPOSE 8000
CMD ["python", "app_producer.py"]