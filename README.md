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
    ENV=prod KNOWLEDGE_URLS=https://gosamurai.ai/,https://gosamurai.ai/payments python src/vdb.py
    ```

4. Run the script you want from the `bots` folder. Example:

    ```bash
    ENV=prod python src/bots/chain_s2.py
    ```
