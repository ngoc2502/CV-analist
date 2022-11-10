FROM python:3.9
WORKDIR /app

COPY . /app
COPY requirements.txt ./requirements

# steps needed for scipy
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev libc-dev build-essential
RUN pip install --upgrade pip

#The cache is usually useless in a Docker image, so shrink the image size by disabling the cache.
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_lg


CMD ["python3","app.py"]
