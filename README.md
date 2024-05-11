# REsolution 🧙🏻‍♂️

*Chatbot that resolves the customer problems*

## Setup

1. Install AWS SAM
   CLI ([tutorial](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
2. Run Backend via
    ```bash
    docker run --env-file .env.prod resolution-api:latest
    ```

## Developer Setup

1. Create environment file(s)
   Each environment has its own configuration file. `.env.local` for local, `.env.prod` for Production.
   Create each file in the root of the repo with all the necessary variables (look
   at [settings.py](server/settings.py)).

2. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

3. Initialize the Vector Database with default data

   If you want to add your own data, provide the website URL via KNOWLEDGE_URL, like this:

    ```bash
    KNOWLEDGE_URLS=https://gosamurai.ai/,https://gosamurai.ai/payments python server/run.py vdb samurai --crawl_depth=1
    ```

   The first parameter is the type of the operation, the second is the name of the organization.

   Also, you can provide the crawling depth via `--crawl_depth=N`, where N denotes the number of nested levels of pages
   to crawl. By default, it's disabled.

4. Chat with the REsolution bot

    ```bash
    python server/run.py chat samurai
    ```

5. Chat with the Librarian bot

    ```bash
    python server/run.py librarian samurai
    ```

6. Save data to VDB from URLs

   a. Add the files to the `server/upload` directory

   b. Run the command
    ```bash
    KNOWLEDGE_URLS=https://link1.com,http://link2.com python server/run.py vdb <org_name> --crawl_depth <N>
    ```
    where `KNOWLEDGE_URLS` is the comma separated list of documentation links to scan,
    `<org_name>` is the name of the organization and `<N>` is the integer denoting the depth of
    links to follow. The command will add the data from the files to the VDB under the given org.

7. Save data to VDB from the file

   a. Add the files to the `server/upload` directory

   b. Run the command
    ```bash
    python server/run.py vdb <org_name> --store_files
    ```
    where `<org_name>` is the name of the organization. The command will add the data from the files to the VDB under the given org.

## Development

* [Docs](docs/README.md)
* [Frontend instructions](frontend/README.md)

## Roadmap

### 0.8 alpha release

Planning.

We want to provide test environments to prospect clients. Simple chat window with the chat already configured for their
company needs.

### Basic components:

1. ✅ Org support
2. ✅ Chat is attached to current org
   It's easier to make accounts bound to the Org. Otherwise, we'll probably need to bind orgs and the databases to the
   URLs, which is complex and complicated. We should have boilerplate code for authentication available.
3. ✅ Save chat history in DB
