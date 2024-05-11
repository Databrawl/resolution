# Database

## Dumping initial PostgreSQL schema with Supabase generated tables:

```bash
pg_dump -h localhost -p 54322 -U postgres -d postgres --schema-only --no-owner --no-acl > init.sql
```

I still had to remove some objects that were created somehow and thus caused duplication errors:

```sql
    CREATE FUNCTION vault.secrets_encrypt_secret_secret() RETURNS trigger
        LANGUAGE plpgsql
        AS $$
            BEGIN
                    new.secret = CASE WHEN new.secret IS NULL THEN NULL ELSE
                CASE WHEN new.key_id IS NULL THEN NULL ELSE pg_catalog.encode(
                  pgsodium.crypto_aead_det_encrypt(
                    pg_catalog.convert_to(new.secret, 'utf8'),
                    pg_catalog.convert_to((new.id::text || new.description::text || new.created_at::text || new.updated_at::text)::text, 'utf8'),
                    new.key_id::uuid,
                    new.nonce
                  ),
                    'base64') END END;
            RETURN new;
            END;
            $$;

    CREATE VIEW vault.decrypted_secrets AS
     SELECT secrets.id,
        secrets.name,
        secrets.description,
        secrets.secret,
            CASE
                WHEN (secrets.secret IS NULL) THEN NULL::text
                ELSE
                CASE
                    WHEN (secrets.key_id IS NULL) THEN NULL::text
                    ELSE convert_from(pgsodium.crypto_aead_det_decrypt(decode(secrets.secret, 'base64'::text), convert_to(((((secrets.id)::text || secrets.description) || (secrets.created_at)::text) || (secrets.updated_at)::text), 'utf8'::name), secrets.key_id, secrets.nonce), 'utf8'::name)
                END
            END AS decrypted_secret,
        secrets.key_id,
        secrets.nonce,
        secrets.created_at,
        secrets.updated_at
       FROM vault.secrets;
```

## Restoring the dump

```bash
psql -h localhost -p 54322 -U postgres -d postgres < supabase/dump-data-06.01.2024.sql
```

## Session architecture

Using `scoped_session` didn't work since this object keeps references to the initial DB URL in factories.
Besides, it's an unnecessary complexity, as we can simply store the session in the context variable.

**Update:** Since we're using Serverless architecture, we don't need to worry about concurrency (all requests run in
separate invocations of lambda), so we can just use a global session object.

# AWS

## Infra TL;DR

We run on AWS Fargate, which is an auto-provisioning service on top of ECS. It's a serverless service, which means we
don't need to worry about the underlying infrastructure.

The service is accessed via an Application Load Balancer (ALB) called `GateKeeper`. It routes both
HTTP and HTTPS traffic to the Target Group consisting of only one target - the ECS cluster. The target
group forwards any traffic to the 5050 port of the container. So any traffic ends up uniformly
in the same place.

## User configuration

I went with new IAM Identity Center setup, which is a successor of AWS SSO. It's now a recommended way
of managing user access to AWS resources, including AWS CLI.

1. Created a new IAM Identity user for myself (called it Sergey Mosin, `serge-guardian`).
2. Created a Permission Set `PowerUserAccess`.
3. Assigned the permission set to the user in the `AWS Accounts` section in the dashboard.
4. Completed aws cli setup via `aws configure sso` command.

Now in the `~/.aws/config` file I have profile `serge-guardian-admin` section.
First, in order to authenticate in AWS SSO tool, you need to launch:
```
aws sso login --sso-session serge-guardian
```

In order to use this profile and the new REsolution AWS account, aws cli commands need to include
`--profile serge-guardian-admin` flag, like this:

```bash
aws s3 ls --profile serge-guardian-admin
```

## SAM CLI

1. `sam init` - only in the very beginning, to create a new project.
2. `sam build` - to build the project. You can use `--use-container` flag to build in a Docker container. Good for
   isolation.
3. `sam deploy --profile=<profile_name>` - to deploy the project. You can use `--guided` flag to configure the
   deployment step-by-step.
   The configuration will be written to the `samconfig.toml` file, so it doesn't need to be repeated.

For local testing, the following commands are quite useful:

1. `sam local start-api` will start a local server on port 3000.
   * `sam local start-api --env-vars env.json --port 5050` - start with env vars on 5050 port
2. `sam local invoke --env-vars env.json --event <path_to_event>.json` - for local testing.
   [Here's detailed docs](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-invoke.html).

## ECR (Elastic Container Registry)

1. `docker build -t resolution-api:latest .` - build the image (from `server` directory)
   * `docker buildx build --platform linux/amd64,linux/arm64 --push -t 375747807787.dkr.ecr.us-east-1.amazonaws.com/resolution .` - build the image for multiple platforms / need to login (see below) first
2. `aws ecr get-login-password --region us-east-1 --profile serge-guardian-admin | docker login --username AWS --password-stdin 375747807787.dkr.ecr.us-east-1.amazonaws.com`
   logs in docker to the ECR, so it can push images there.
3`aws ecr create-repository --repository-name resolution --region us-east-1 --profile serge-guardian-admin`
   creates container called `resolution-hub` in the `us-east-1` region.
4`docker tag resolution-api:latest 375747807787.dkr.ecr.us-east-1.amazonaws.com/resolution`
   tag the image
5`docker push 375747807787.dkr.ecr.us-east-1.amazonaws.com/resolution` - push the image to the ECR
   This is the operation to be repeated


## EC2
1. [Local] Push docker image from local
2. [Local] Connect to the EC2 instance via ssh:
    ```bash
    ssh -i "REsolution-API-EC2.pem" ec2-user@ec2-54-209-19-205.compute-1.amazonaws.com
    ```
3. [EC2] Pull docker image from ECR
   ```bash
    docker pull 375747807787.dkr.ecr.us-east-1.amazonaws.com/resolution
   ```
4. [EC2] Run the container
   ```bash
   docker run --env-file .env.prod -t -d -p 80:5050 375747807787.dkr.ecr.us-east-1.amazonaws.com/resolution
   ```

## Helper commands

1. Quick 
### Template structure

`template.yaml` is the main file, where all the resources are defined.

Secret configuration is explained [here](https://stackoverflow.com/a/65777849/1573766).
