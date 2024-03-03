cd ../deploy || exit

sam build
# make sure you have env.json file in deploy directory
sam local start-api --env-vars env.json --port 5050
