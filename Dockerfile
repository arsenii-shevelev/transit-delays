FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY positions.py ingest.py ./
RUN useradd --system app
USER app
CMD ["python", "ingest.py"]
