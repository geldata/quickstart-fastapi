import json
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Flashcards API")

DATA_DIR = Path(__file__).parent / "data"
DECKS_FILE = DATA_DIR / "decks.json"

DATA_DIR.mkdir(exist_ok=True)
if not DECKS_FILE.exists():
    DECKS_FILE.write_text("[]")


# Pydantic models
class CardCreate(BaseModel):
    front: str
    back: str


class Card(CardCreate):
    id: uuid.UUID


class DeckBase(BaseModel):
    name: str
    description: str | None = None


class DeckCreate(DeckBase):
    cards: list[CardCreate]


class Deck(DeckBase):
    id: uuid.UUID
    cards: list[Card]


def read_decks() -> list[Deck]:
    content = DECKS_FILE.read_text()
    data = json.loads(content)
    return [Deck(**deck) for deck in data]


def write_decks(decks: list[Deck]) -> None:
    data = [deck.model_dump() for deck in decks]
    DECKS_FILE.write_text(json.dumps(data, indent=2))


@app.get("/decks")
async def get_decks():
    return read_decks()


@app.get("/decks/{deck_id}")
async def get_deck(deck_id: uuid.UUID):
    decks = read_decks()
    deck = next((deck for deck in decks if deck.id == deck_id), None)
    if not deck:
        raise HTTPException(status_code=404, detail=f"Deck with id {deck_id} not found")
    return deck


@app.post("/decks/import")
async def import_deck(deck: DeckCreate):
    decks = read_decks()
    new_deck = Deck(
        id=uuid.uuid4(),
        name=deck.name,
        description=deck.description,
        cards=[Card(id=uuid.uuid4(), **card.model_dump()) for card in deck.cards],
    )
    decks.append(new_deck)
    write_decks(decks)
    return new_deck


@app.put("/decks/{deck_id}")
async def update_deck(deck_id: uuid.UUID, deck_update: DeckBase):
    decks = read_decks()
    deck = next((deck for deck in decks if deck.id == deck_id), None)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    deck.name = deck_update.name
    deck.description = deck_update.description
    write_decks(decks)
    return deck


@app.post("/decks/{deck_id}/cards")
async def add_card(deck_id: uuid.UUID, card: CardCreate):
    decks = read_decks()
    deck = next((deck for deck in decks if deck.id == deck_id), None)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    new_card = Card(id=uuid.uuid4(), **card.model_dump())
    deck.cards.append(new_card)
    write_decks(decks)
    return new_card


@app.delete("/decks/{deck_id}/cards/{card_id}")
async def delete_card(deck_id: uuid.UUID, card_id: uuid.UUID):
    decks = read_decks()
    deck = next((deck for deck in decks if deck.id == deck_id), None)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    deck.cards = [card for card in deck.cards if card.id != card_id]
    write_decks(decks)
    return {"message": "Card deleted"}
