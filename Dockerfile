# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

FROM python:3.9-slim-buster

# Prevents Python from writing pyc files.

WORKDIR /app
# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN apt-get update && apt-get install -y build-essential
COPY ./requirements.txt /app
RUN   pip install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt
RUN pip install firebase_admin

COPY . .

# Copy the source code into the container.
COPY . .

ENV PORT 8080
ENV HOST 0.0.0.0
# Expose the port that the application listens on.
EXPOSE 8080

# Run the application.
CMD ["waitress-serve", "--call", "flaskr:create_app"]
#CMD ["flask", "--app", "flaskr", "init-db"]
