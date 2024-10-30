# Use a base image
FROM python:3.9-slim

# Set up working directory
WORKDIR /app

# Copy files
COPY . /app

# Install requirements
RUN pip install -r requirements.txt

# Expose the port Flask will run on
EXPOSE $PORT

# Run the Flask app
CMD ["python", "app.py"]
