# syntax=docker/dockerfile:1
FROM python:3.7-alpine
WORKDIR /code
ENV REDIS_SERVER='redis'
RUN apk add --no-cache gcc musl-dev linux-headers
RUN apk add libffi-dev
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
COPY config.py config.py
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]