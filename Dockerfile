FROM python:3.11-slim

WORKDIR /python

COPY requirements.txt /python

RUN pip install --no-cache-dir -r requirements.txt

COPY /app /python

EXPOSE 8001

CMD [ "python", "./main.py" ]