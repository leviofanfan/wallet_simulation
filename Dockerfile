FROM python:3.10

WORKDIR app/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
STOPSIGNAL SIGTERM
EXPOSE 8000/tcp

CMD ["uvicorn", "app.main:app", "--reload", "--host", "localhost", "--port", "8000"]