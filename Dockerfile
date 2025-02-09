# Use a Python base image with the required version
FROM python:3.9.21

LABEL maintainer="Tanmay Kumar <tanmay44a@gmail.com>"
# Set environment variables

# Set the working directory inside the container
WORKDIR /app

# Compy the entire directory into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN prisma generate
# Installl corm (to schedule tasks)
# RUN apt-get update && apt-get install -y cron

#Add the cron job to run main.py every hour
# RUN echo "0 * * * * /usr/local/bin/python /app/main.py >> /proc/1/fd/1 2>&1" > /etc/cron.d/main-job
# Apply cron job and give necessary permissions
# RUN chmod 0644 /etc/cron.d/main-job
# RUN crontab /etc/cron.d/main-job

# Start cron service and run the application
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]

