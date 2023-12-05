# opp-api

## PM1
* Please see design-documents folder

## PM2
* For REST APIs, please see src/routers, we build 11 public-facing APIs for card/payment/transaction model
* For database, we use Sqlite3 for our project. More details are included in src/db/database.py
* For WSGI, we use Univorn as shown below:
![Screenshot](Uvicorn.png)

## PM3
* The API call using curl is successful as shown below:
![Screenshot](API_call.png)  
* All tests for ReST APIs are included in tests folder

## PM4A
* Build the Docker image:
```
docker build -t opp-api-image .
```
* Running the Docker Container:

Run the Docker container, exposing port 8000:

```
docker run -p 8000:8000 opp-api-image
```

## PM4B
* Public Url: http://ec2-3-90-144-11.compute-1.amazonaws.com:8000/docs
* To push to ECR run:
```
make push-to-ecr
```
in root directory

## PM5
Demo Video: https://www.youtube.com/watch?v=fz4tVLLMN5w
