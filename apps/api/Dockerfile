FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY growthos ./growthos
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "growthos.main:app", "--host", "0.0.0.0", "--port", "8000"]

