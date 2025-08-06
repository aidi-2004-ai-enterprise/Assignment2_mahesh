# Start with a base Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This is a common practice for better Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# This is the corrected COPY command.
# It copies the local `app/data` directory to `/app/data` in the container.
COPY app/data/ ./data/

# Copy your application code
COPY penguin_app/ ./penguin_app/

# Expose the port the application will run on
EXPOSE 8080

# The command to start the Uvicorn server
CMD ["uvicorn", "penguin_app.main:app", "--host", "0.0.0.0", "--port", "8080"]
