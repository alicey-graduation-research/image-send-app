FROM python:3.9.10

WORKDIR /opt/app
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y libgl1-mesa-dev \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt ./requirements.txt
ADD app/ .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

ENTRYPOINT [ "python", "app.py" ] 