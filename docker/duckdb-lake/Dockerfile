FROM python:3.11-slim

RUN pip install --no-cache-dir duckdb==1.0.0 boto3 pyarrow pandas

WORKDIR /workspace
CMD ["tail", "-f", "/dev/null"]
