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
    KNOWLEDGE_URLS=https://gosamurai.ai/,https://gosamurai.ai/payments python src/main.py vdb samurai
    ```

   The first parameter is the type of the operation, the second is the name of the organization.
   Available operations:

   1. `vdb` - Vector Database initialization
   2. `librarian` - chat with the Librarian bot
   3. `chat` - chat with the support bot, customer mode
