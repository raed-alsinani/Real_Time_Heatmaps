FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=Real_Time_Heatmaps.settings.prod
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /app/
WORKDIR /app
RUN pip install --upgrade pip \
    && pip install -r requirements.txt


COPY . /app/


EXPOSE 8000

