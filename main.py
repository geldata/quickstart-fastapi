from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
from pathlib import Path

app = FastAPI(title="Flashcards API")

DATA_DIR = Path(__file__).parent / "data"
DECKS_FILE = DATA_DIR / "decks.json"

DATA_DIR.mkdir(exist_ok=True)
if not DECKS_FILE.exists():
    DECKS_FILE.write_text("[]")

# Pydantic models
class CardBase(BaseModel):
    front: str
    back: str

class Card(CardBase):
    id: str

class DeckBase(BaseModel):
    name: str
    description: Optional[str] = None

class DeckCreate(DeckBase):
    cards: List[CardBase]

class Deck(DeckBase):
    id: str
    cards: List[Card]

def read_decks() -> List[Deck]:
    content = DECKS_FILE.read_text()
    data = json.loads(content)
    return [Deck(**deck) for deck in data]

def write_decks(decks: List[Deck]) -> None:
    data = [deck.model_dump() for deck in decks]
    DECKS_FILE.write_text(json.dumps(data, indent=2))

@app.get("/decks", response_model=List[Deck])
async def get_decks():
    return read_decks()

@app.get("/decks/{deck_id}", response_model=Deck)
async def get_deck(deck_id: str):
    decks = read_decks()
    deck = next((deck for deck in decks if deck.id == deck_id), None)
    if not deck:
        raise HTTPException(status_code=404, detail=f"Deck with id {deck_id} not found")
    return deck

@app.post("/decks/import", response_model=Deck)
async def import_deck(deck: DeckCreate):
    decks = read_decks()
    new_deck = Deck(
        id=str(uuid.uuid4()),
        name=deck.name,
        description=deck.description,
        cards=[Card(id=str(uuid.uuid4()), **card.model_dump()) for card in deck.cards]
    )
    decks.append(new_deck)
    write_decks(decks)
    return new_deck

@app.put("/decks/{deck_id}", response_model=Deck)
async def update_deck(deck_id: str, deck_update: DeckBase):
    decks = read_decks()
    deck = next((deck for deck in decks if deck.id == deck_id), None)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    deck.name = deck_update.name
    deck.description = deck_update.description
    write_decks(decks)
    return deck

@app.post("/decks/{deck_id}/cards", response_model=Card)
async def add_card(deck_id: str, card: CardBase):
    decks = read_decks()
    deck = next((deck for deck in decks if deck.id == deck_id), None)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    new_card = Card(id=str(uuid.uuid4()), **card.model_dump())
    deck.cards.append(new_card)
    write_decks(decks)
    return new_card

@app.delete("/decks/{deck_id}/cards/{card_id}")
async def delete_card(deck_id: str, card_id: str):
    decks = read_decks()
    deck = next((deck for deck in decks if deck.id == deck_id), None)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    deck.cards = [card for card in deck.cards if card.id != card_id]
    write_decks(decks)
    return {"message": "Card deleted"} 