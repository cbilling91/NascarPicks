# Use the official Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code into the container
COPY . .

# Download the CockroachDB Cloud root CA to ~/.postgresql/root.crt so libpq
# can connect with sslmode=verify-full (same mechanism as the notifications image)
RUN python3 copy_root_cert.py

# Expose the port the FastAPI application will run on
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
