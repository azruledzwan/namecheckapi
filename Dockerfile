FROM --platform=linux/x86-64 python:3.9

RUN python3 -m venv /opt/venv
COPY requirements.txt / 
RUN . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y curl vim

WORKDIR /app 
COPY . /app

EXPOSE 8000
ENTRYPOINT ["sh", "/app/entrypoint.sh"]