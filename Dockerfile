FROM python:3.8.6-buster
RUN apt-get update && apt-get upgrade -y
RUN apt-get install vim -y
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--workers=3", "--bind", "0.0.0.0:8080",  "wsgi:app", "run"]
