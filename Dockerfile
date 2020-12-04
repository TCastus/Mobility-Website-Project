FROM python:3.9-slim

EXPOSE 8000

WORKDIR /app

RUN apt update && apt install -y gcc
RUN pip install --upgrade pip

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

RUN chmod +x /app/docker-conf/run.sh
CMD /app/docker-conf/run.sh
