# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install dependencies if requirements.txt exists
RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt found"

# Expose port 5051
EXPOSE 5051

# Set environment variable (optional)
ENV PORT=5051

# Run the application
CMD ["python", "app.py"]
