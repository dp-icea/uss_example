FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000

COPY ./ /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
