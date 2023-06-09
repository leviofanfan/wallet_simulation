FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
STOPSIGNAL SIGTERM
EXPOSE 8000/tcp

CMD ["uvicorn", "main:app", "--reload", "--host", "localhost", "--port", "8000"]