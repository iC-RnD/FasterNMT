# set base image (host OS)
FROM python:3.7
EXPOSE 8000

RUN apt-get update
RUN apt install build-essential libicu-dev -y
RUN mkdir /app
WORKDIR /app

COPY requirements_api.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY config /app/config
COPY iclib /app/iclib
COPY entity /app/entity
COPY function /app/function
COPY api.py /app
RUN rm -r ~/.cache/pip/*
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "3"]