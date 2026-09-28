FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all the backend files into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Start the Flask app with Gunicorn (4 workers) on port 7860
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:app"]
