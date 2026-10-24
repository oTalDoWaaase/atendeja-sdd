FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 atendeja
COPY app ./app
USER atendeja
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Imagem de testes: estende a de execução com dependências de desenvolvimento.
FROM runtime AS test
USER root
COPY requirements-dev.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
COPY scripts ./scripts
# /app pertence ao root; o arquivo de dados da cobertura vai para um local gravável.
ENV COVERAGE_FILE=/tmp/.coverage
USER atendeja
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--cov"]
