FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /{DIR_NAME}

COPY requirements.txt /{DIR_NAME}/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn

COPY . /{DIR_NAME}/
