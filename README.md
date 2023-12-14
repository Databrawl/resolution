# Guardian

*Chatbot that protects your customers and your team*

## Setup

1. Create environment file(s)
   Each environment has its own configuration file. `local.env` for local, `prod.env` for
   Production.
   Create each file in the root of the repo with all the necessary variables (look
   at `config/settings.py`).

2. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

3. Initialize the Vector Database with default data

   If you want to add your own data, provide the website URL via KNOWLEDGE_URL, like this:

    ```bash
    KNOWLEDGE_URLS=https://gosamurai.ai/,https://gosamurai.ai/payments python server/main.py vdb samurai --crawl_depth=1
    ```

   The first parameter is the type of the operation, the second is the name of the organization.

   Also, you can provide the crawling depth via `--crawl_depth=N`, where N denotes the number of nested levels of pages
   to crawl. By default, it's disabled.

4. Chat with the Guardian bot

    ```bash
    python server/main.py chat samurai
    ```

5. Chat with the Librarian bot

    ```bash
    python server/main.py librarian samurai
    ```