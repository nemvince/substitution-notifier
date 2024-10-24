FROM python:3.12-alpine

WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY app /app/

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
