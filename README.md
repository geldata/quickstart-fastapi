# Flashcards API

A FastAPI backend for the Flashcards application.

## Getting Started

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the Gel database:

```bash
gel project init
```

4. Run the development server:
```bash
uvicorn main:app --reload
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
curl -X DELETE http://localhost:8000/cards/{card_id}
```

Note: Replace `{card_id}` with actual IDs in the above commands. 
