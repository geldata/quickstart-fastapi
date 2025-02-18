import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from edgedb import create_async_client

app = FastAPI(title="Flashcards API")

client = create_async_client()


# Pydantic models
class CardBase(BaseModel):
    front: str
    back: str
    order: Optional[int] = None


class Card(CardBase):
    id: uuid.UUID


class DeckBase(BaseModel):
    name: str
    description: Optional[str] = None


class DeckCreate(DeckBase):
    cards: List[CardBase]


class Deck(DeckBase):
    id: uuid.UUID
    cards: List[Card]


@app.get("/decks", response_model=List[Deck])
async def get_decks():
    decks = await client.query("""
       SELECT Deck {
           id,
           name,
           description,
           cards := (
               SELECT .cards {
                   id,
                   front,
                   back
               }
               ORDER BY .order
           )
       }
   """)
    return decks


@app.get("/decks/{deck_id}", response_model=Deck)
async def get_deck(deck_id: str):
    deck = await client.query_single(
        """
        SELECT Deck {
            id,
            name,
            description,
            cards := (
                SELECT .cards {
                    id,
                    front,
                    back,
                    order
                }
                ORDER BY .order
            )
        }
        FILTER .id = <uuid>$id
    """,
        id=deck_id,
    )

    if not deck:
        raise HTTPException(status_code=404, detail=f"Deck with id {deck_id} not found")
    return deck


@app.post("/decks/import", response_model=Deck)
async def import_deck(deck: DeckCreate):
    cards_data = [(c.front, c.back, i) for i, c in enumerate(deck.cards)]

    new_deck = await client.query_single(
        """
        select (
            with
                cards := <array<tuple<str, str, int64>>>$cards_data
            insert Deck {
                name := <str>$name,
                description := <optional str>$description,
                cards := (
                    for card in array_unpack(cards)
                    union (
                        insert Card {
                            front := card.0,
                            back := card.1,
                            order := card.2
                        }
                    )
                )
            }
        ) { ** }
        """,
        name=deck.name,
        description=deck.description,
        cards_data=cards_data,
    )

    return new_deck


@app.put("/decks/{deck_id}", response_model=Deck)
async def update_deck(deck_id: str, deck_update: DeckBase):
    # Build update sets based on provided fields
    sets = []
    params = {"id": deck_id}

    if deck_update.name is not None:
        sets.append("name := <str>$name")
        params["name"] = deck_update.name

    if deck_update.description is not None:
        sets.append("description := <optional str>$description")
        params["description"] = deck_update.description

    if not sets:
        return await get_deck(deck_id)

    query = """
        select(
            update Deck
            filter .id = <uuid>$id
            set { %s }
        ) { ** }
    """ % ", ".join(sets)

    updated_deck = await client.query_single(query, **params)

    if not updated_deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    return updated_deck


@app.post("/decks/{deck_id}/cards", response_model=Deck)
async def add_card(deck_id: str, card: CardBase):
    # Get max order and increment
    deck = await client.query_single(
        """
        select Deck {
            max_order := max(.cards.order)
        }
        filter .id = <uuid>$id
        """,
        id=deck_id,
    )

    new_order = (deck.max_order or -1) + 1

    new_card = await client.query_single(
        """
        insert Card {
            front := <str>$front,
            back := <str>$back,
            order := <int64>$order,
        }
        """,
        front=card.front,
        back=card.back,
        order=new_order,
    )

    new_deck = await client.query_single(
        """
        select(
            update Deck
            filter .id = <uuid>$id
            set {
                cards += (select Card { id, front, back } filter .id = <uuid>$card_id)
            }
        ) { ** }
        """,
        id=deck_id,
        card_id=new_card.id,
    )

    if not new_card:
        raise HTTPException(status_code=404, detail="Deck not found")

    return new_deck


@app.delete("/cards/{card_id}", response_model=str)
async def delete_card(card_id: str):
    deleted = await client.query(
        """
        delete Card
        filter
            .id = <uuid>$card_id
        """,
        card_id=card_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Card not found")

    return "Card deleted"
