FROM python:3.11-slim

RUN pip install --no-cache-dir dagster dagster-webserver

WORKDIR /opt/dagster/app
EXPOSE 3000
CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]
