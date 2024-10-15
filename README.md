# Rooms Bot in InNoHassle ecosystem

## Development

### Getting started

1. Install Python 3.12

2. Install Poetry

3. Install dependencies
    ```bash
    poetry install
    ```

4. Set up pre-commit hook
    ```bash
    poetry run pre-commit install
    ```

5. Set up settings file.
    ```bash
    cp example.env .env
    ```
   Insert your bot token and API token (see [API's README](https://github.com/one-zero-eight/rooms/blob/main/README.md) to obtain it).

## Run

Run an [API](https://github.com/one-zero-eight/rooms/) instance.

Then, run the bot:
```bash
poetry run python -m src.bot.main
```
