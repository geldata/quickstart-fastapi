# Flashcards API

A FastAPI backend for the Flashcards application.

## Getting Started

We will use `uv` to create a virtual environment, and install our dependencies.

```bash
uv venv
uv sync
```

You can then run the FastAPI dev server

```bash
uv run fastapi dev
# or with your venv
source .venv/bin/activate
fastapi dev
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### List all decks
```bash
curl http://localhost:8000/decks
```

### Get a specific deck
```bash
curl http://localhost:8000/decks/{deck_id}
```

### Import a new deck
```bash
curl -X POST http://localhost:8000/decks/import \
  -H "Content-Type: application/json" \
  -d @data/sample-deck.json
```

### Update deck details
```bash
curl -X PUT http://localhost:8000/decks/{deck_id} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Deck Name",
    "description": "Updated description"
  }'
```

### Add a card to a deck
```bash
curl -X POST http://localhost:8000/decks/{deck_id}/cards \
  -H "Content-Type: application/json" \
  -d '{
    "front": "What is the capital of France?",
    "back": "Paris"
  }'
```

### Delete a card from a deck
```bash
curl -X DELETE http://localhost:8000/decks/{deck_id}/cards/{card_id}
```

Note: Replace `{deck_id}` and `{card_id}` with actual IDs in the above commands. 