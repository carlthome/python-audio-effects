# This container is for developing locally inside it.
FROM python:3.7
RUN apt-get update && apt-get install -y sox
RUN pip install librosa
COPY . .
RUN pip install -e .[test]