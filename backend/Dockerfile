FROM python:3.7-slim

LABEL author="iricshkin"
LABEL maintainer="Irina Fok"

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip3 install -r ./requirements.txt --no-cache-dir

# COPY ./ .

COPY . ./

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
