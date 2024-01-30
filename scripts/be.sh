cd ../deploy || exit

sam build --use-container
# make sure you have env.json file in deploy directory
sam local start-api --env-vars env.json --port 5050