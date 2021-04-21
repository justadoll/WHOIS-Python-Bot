FROM python:buster

RUN mkdir -p /usr/src/app/
RUN mkdir -p /usr/src/app/files
WORKDIR /usr/src/app/

COPY . /usr/src/app/
RUN pip3 install -r requirements.txt

CMD ["python3","main.py"]
