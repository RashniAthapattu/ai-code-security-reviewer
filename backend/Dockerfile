FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Run as a normal user, not root. Semgrep needs a writable home folder.
RUN useradd --create-home app
WORKDIR /app

# Install the dependencies first, so this slow step is cached
# until pyproject.toml changes.
COPY pyproject.toml ./
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']))" > requirements.txt \
    && pip install -r requirements.txt

# Then the application code and the Semgrep rules
COPY app ./app
COPY rules ./rules

USER app
EXPOSE 8000

# Hosts such as Render set PORT; locally it defaults to 8000.
# --proxy-headers makes the visitor's real address visible behind the host's
# proxy, which the per-visitor rate limit needs.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips=*"]
