FROM python:3.6

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY uploads ./
COPY convert.py ./
COPY server.py ./

CMD [ "python", "./server.py" ]
