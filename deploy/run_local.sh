# make sure you have env.json file in this directory

sam build --use-container
sam local start-api --env-vars env.json --port 5050
