# Use the official Airflow image
FROM apache/airflow:2.2.0

# Set environment variables for Airflow
ENV AIRFLOW_HOME=/opt/airflow

# Copy requirements file to install dependencies
COPY requirements.txt /requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --no-deps -r /requirements.txt

# Copy requirements file to install dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the Airflow configuration and DAGs into the container
COPY ./dags /opt/airflow/dags
# COPY ./airflow.cfg /opt/airflow/airflow.cfg

# Expose ports for the Airflow UI and scheduler
EXPOSE 8080

# Start Airflow Web Server and Scheduler
CMD ["bash", "-c", "airflow standalone"]


