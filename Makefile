image: Dockerfile
	docker build -t opp .

run-app-local:
	docker run -p 8000:8000 opp
 