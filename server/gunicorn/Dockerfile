FROM python:3.6

EXPOSE 8000

RUN pip3 install gunicorn json-logging-py
RUN pip3 install hug -U

RUN python -m pip install --upgrade pip
RUN pip3 install http://download.pytorch.org/whl/cu75/torch-0.2.0.post3-cp36-cp36m-manylinux1_x86_64.whl 
RUN pip3 install torchvision
RUN pip3 install redis pymongo

WORKDIR /src

RUN ls -l /src

CMD gunicorn --reload --log-config logging.conf --workers=2 --bind=0.0.0.0:8000 __init__:__hug_wsgi__