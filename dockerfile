FROM python:3.9
WORKDIR /app


# steps needed for scipy
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev libc-dev build-essential

#The cache is usually useless in a Docker image, so shrink the image size by disabling the cache.
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN python3 -m spacy download en_core_web_lg

COPY . .
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]