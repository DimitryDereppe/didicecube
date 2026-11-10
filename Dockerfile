# Image de développement de l'application Django (production : voir README, à compléter).
FROM python:3.14-slim

# Pas de fichiers .pyc, journaux affichés tout de suite.
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
# Image de développement : outils de vérification compris (ruff, pip-audit).
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

# L'application ne tourne pas en root.
RUN useradd --create-home appli && chown -R appli /app
USER appli

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
