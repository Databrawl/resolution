set -a
source ../.env.prod
set +a
cd ../client
yarn dev
