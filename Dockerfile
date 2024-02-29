# Use an official Python runtime as a parent image with a specific minor version tag
FROM python:3.11.0-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Create a non-root user and change ownership of work directory
RUN adduser --disabled-password --gecos '' magika_user
RUN chown -R magika_user /usr/src/app
USER magika_user

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["gunicorn", "-b", "[::]:5000", "app:app"]
