FROM python:3.10-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git curl && \
    apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt

RUN pip install -U pip && pip install -U -r requirements.txt
WORKDIR /AV-FILE-TO-LINK-PRO
COPY . /AV-FILE-TO-LINK-PRO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/api/health || exit 1

CMD ["python", "bot.py"]
