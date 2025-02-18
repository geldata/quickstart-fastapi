import edgedb

client = edgedb.create_async_client()


client.query("""
     insert Deck { name := "I am one" }
 """)

client.query("""
         insert Deck { name := "I am two" }
     """)

decks = client.query("""
     select Deck {
         id,
         name
     }
 """)

for deck in decks:
    print(f"ID: {deck.id}, Name: {deck.name}")

client.query("delete Deck")

client.close()
