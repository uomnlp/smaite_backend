# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /smaite_docker/backend

COPY model/. ./model/

RUN apt-get update && apt-get install -y python3-dev build-essential

# A layer for updating dependencies
COPY requirements.txt ./ 
RUN pip install -r ./requirements.txt

# A layer for code changes
COPY .env factchecker.py  server.py ./ 

EXPOSE 8000
CMD ["gunicorn", "-b", ":8000","--timeout","120", "server:app"]