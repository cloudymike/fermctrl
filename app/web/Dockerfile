FROM ubuntu:jammy
WORKDIR /code
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV REDIS_SERVER='redis'

RUN apt update
RUN apt -y install python3
RUN python3 --version
RUN apt -y install pip
RUN pip3 install --upgrade pip

#RUN pip3 install matplotlib 

COPY requirements.txt requirements.txt
COPY config.py config.py
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]