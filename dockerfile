# Use an official Python runtime as the base image
FROM python:3.12.10-slim

# Create and set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Flask app code into the container
COPY ./static /app/static
COPY ./templates /app/templates
COPY ./main.py /app/
COPY ./config.py /app/

# Expose the port that Flask will run on
EXPOSE 5000

# Use gunicorn to serve the app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app", "--log-level", "debug"]
