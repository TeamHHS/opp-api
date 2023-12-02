image: Dockerfile
	docker build -t opp .

run-app-local:
	docker run -p 8000:8000 opp
 
logout-docker:
	docker logout

login-docker:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/o7p5f0w8

tag-image:
	docker tag opp:latest public.ecr.aws/o7p5f0w8/opp:latest

push-iamge-to-ecr:
	docker push public.ecr.aws/o7p5f0w8/opp:latest

push-to-ecr:
	make logout-docker && make login-docker && make image && make tag-image && make push-iamge-to-ecr