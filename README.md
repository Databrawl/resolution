# Guardian
*Chatbot that protects your customers and your team*

## Setup

1. Create environment file

    Create a `.env` file in the root of the repo with all the necessary variables (look at `config/settings.py`).

2. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

3. Initialize the Vector Database with default data

    ```bash
    python src/vdb.py
    ```
   
   If you want to add your own data, provide the website URL via KNOWLEDGE_URL, like this:
   
   ```bash
    KNOWLEDGE_URL=https://gosamurai.ai/ python src/vdb.py
    ```

4. Run the script you want from the `bots` folder. Example:

    ```bash
    python src/bots/chain_0.py
    ```
