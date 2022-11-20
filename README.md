# CV-analist
Visit : [CV-analist](http://cv.uway.asia)
# Overview
Extract information from the CV pdf files and matching with the JD file. The higher the percentage score, the better CV fits the JD . The final result will be shown on web, user can dowload as csv file.

# How to run?
## Run on local
### Set up environment:

Build the Docker image
```
docker image build -t flask_docker
```
Run the container
```
docker run -p 5000:5000 -d flask_docker
```
This command runs the container and its embedded application, each on port 5000 using a port-binding approach. The first 5000 is the port that we allocate to the container on our machine. The second 5000 is the port where the application will run on the container.

Or you can also install all packages through requirements.txt file by following
```
pip install -r /path/to/requirements.txt
```
And run app using ```python3 app.py```.
Now You can check your local link on terminal and get the result.

## Deploy on NGINX server
# Documentation
