# Guardian

*Chatbot that protects your customers and your team*

## Setup

1. Install AWS SAM
   CLI ([tutorial](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
2. Go to the `scripts` directory and then run these two commands in separate terminal windows:

    ```bash
    ./be.sh
    ```

    ```bash
    ./fe.sh
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

4. Chat with the Guardian bot

    ```bash
    python server/run.py chat samurai
    ```

5. Chat with the Librarian bot

    ```bash
    python server/run.py librarian samurai
    ```

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
2. Chat is attached to current org
   It's easier to make accounts bound to the Org. Otherwise, we'll probably need to bind orgs and the databases to the
   URLs, which is complex and complicated. We should have boilerplate code for authentication available.
3. Save chat history in DB