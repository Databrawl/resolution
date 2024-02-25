#!/bin/bash

# Check if an argument is provided
if [ $# -eq 0 ]; then
  echo "No environment specified, defaulting to 'prod'"
  ENV="prod"
else
  ENV=$1
fi

set -a
source ../.env.$ENV
set +a
cd ../client
yarn dev
