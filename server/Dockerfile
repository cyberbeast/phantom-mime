FROM python:3

ENV HOME=/home
ENV PYTHONUNBUFFERED=1
WORKDIR $HOME/server

COPY ./src/requirements.txt $HOME/server/
RUN pip install -r requirements.txt



