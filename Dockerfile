# ================= Target: trainer =================
FROM python:3.10-slim AS trainer
WORKDIR /build
ENV PYTHONPATH=/build PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-train.txt .
RUN pip install --no-cache-dir -r requirements-train.txt

COPY src/ ./src/
# Навчання запускається під час docker run, а не docker build
ENTRYPOINT ["python", "-m", "src.train"]
CMD ["--classes", "yes", "no", "up", "down", "--epochs", "10", \
     "--seed", "42", "--data-dir", "/data", "--out", "/artifacts"]


# ================= Target: runtime =================
FROM python:3.10-slim AS runtime
WORKDIR /app
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY src/ ./src/
# Модель береться з каталогу artifacts/, а не з етапу trainer
COPY artifacts/ ./artifacts/

ENV MODEL_PATH=/app/artifacts/model.pt \
    PORT=8000 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import os,urllib.request as u; u.urlopen('http://localhost:%s/health' % os.getenv('PORT','8000'))"

CMD ["sh", "-c", "uvicorn src.api:app --host 0.0.0.0 --port ${PORT}"]