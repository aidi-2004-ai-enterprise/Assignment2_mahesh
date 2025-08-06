FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the penguin_app folder containing main.py
COPY penguin_app/ ./penguin_app/

# Copy the data folder and its contents.
# Place it inside the penguin_app directory inside the container.
COPY app/data/ ./penguin_app/data/

EXPOSE 8080

# The CMD command is correct now because the application is at /app/penguin_app/main.py
CMD ["uvicorn", "penguin_app.main:app", "--host", "0.0.0.0", "--port", "8080"]