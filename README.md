# Example Portainer deployment script

## Install requirements

    apt-get update && apt-get install python-yaml python-requests --assume-yes

or...

    pip install requests yaml


## Configuration

Fill out credentials.yaml with hostname, username, password and endpoint to be used.

## Running

    ./deploy.py --stack-name <Name of Stack> --deploy-version <Docker Image> --tag-parameter <Comma-separated yaml traversal>

NOTE: The last parameter is used to traverse the docker-compose yaml. For example, if your docker-compose contains something like:

    services:
        web:
            image: my-docker-image:latest

then the argument would be: 'services,web,image'
