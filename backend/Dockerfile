FROM python:3.11-slim

WORKDIR /app

# Ganti mirror ke Indonesia untuk lebih cepat
RUN sed -i 's/deb.debian.org/kartolo.sby.datautama.net.id/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]