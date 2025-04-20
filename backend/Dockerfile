FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY . .

RUN pip install pipenv

RUN pipenv install --system --deploy

EXPOSE 5000

CMD ["python", "app.py"]