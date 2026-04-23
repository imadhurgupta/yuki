#!/bin/sh

echo ">> Initializing Database..."
# Run the database creation script. 
# If the DB container isn't ready yet, this might fail, causing the container to restart. 
# This simple retry mechanism is handled by Docker's restart policy.
python create_db.py

echo ">> Starting Gunicorn Server..."
# Bind to 0.0.0.0:5000 so it is accessible outside the container
# 'app:app' refers to the 'app.py' file and the 'app' flask instance inside it
exec gunicorn --bind 0.0.0.0:5000 app:app