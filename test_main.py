import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        temp_decks_file = temp_path / "decks.json"
        temp_decks_file.write_text("[]")

        with (
            patch("main.DATA_DIR", temp_path),
            patch("main.DECKS_FILE", temp_decks_file),
        ):
            yield temp_path


@pytest.fixture
def sample_deck_data():
    """Sample deck data for testing."""
    return {
        "name": "Spanish Vocabulary",
        "description": "Basic Spanish words and phrases",
        "cards": [
            {"front": "Hello", "back": "Hola"},
            {"front": "Goodbye", "back": "Adiós"},
            {"front": "Thank you", "back": "Gracias"},
        ],
    }


@pytest.fixture
def created_deck(client, temp_data_dir, sample_deck_data):
    """Create a deck and return its data."""
    response = client.post("/decks/import", json=sample_deck_data)
    return response.json()


class TestGetDecks:
    """Test the GET /decks endpoint."""

    def test_get_empty_decks(self, client, temp_data_dir):
        """Test getting decks when no decks exist."""
        response = client.get("/decks")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_decks_with_data(self, client, created_deck):
        """Test getting decks when decks exist."""
        response = client.get("/decks")
        assert response.status_code == 200
        decks = response.json()
        assert len(decks) == 1
        assert decks[0]["name"] == "Spanish Vocabulary"
        assert decks[0]["description"] == "Basic Spanish words and phrases"
        assert len(decks[0]["cards"]) == 3


class TestImportDeck:
    """Test the POST /decks/import endpoint."""

    def test_import_deck_success(self, client, temp_data_dir, sample_deck_data):
        """Test successfully importing a new deck."""
        response = client.post("/decks/import", json=sample_deck_data)

        assert response.status_code == 200
        deck = response.json()

        # Check deck structure
        assert "id" in deck
        assert deck["name"] == sample_deck_data["name"]
        assert deck["description"] == sample_deck_data["description"]
        assert len(deck["cards"]) == len(sample_deck_data["cards"])

        # Check each card has an ID and correct content
        for i, card in enumerate(deck["cards"]):
            assert "id" in card
            assert card["front"] == sample_deck_data["cards"][i]["front"]
            assert card["back"] == sample_deck_data["cards"][i]["back"]

    def test_import_deck_without_description(self, client, temp_data_dir):
        """Test importing a deck without description."""
        deck_data = {"name": "Math Facts", "cards": [{"front": "2 + 2", "back": "4"}]}

        response = client.post("/decks/import", json=deck_data)
        assert response.status_code == 200
        deck = response.json()
        assert deck["name"] == "Math Facts"
        assert deck["description"] is None
        assert len(deck["cards"]) == 1

    def test_import_deck_empty_cards(self, client, temp_data_dir):
        """Test importing a deck with no cards."""
        deck_data = {
            "name": "Empty Deck",
            "description": "A deck with no cards",
            "cards": [],
        }

        response = client.post("/decks/import", json=deck_data)
        assert response.status_code == 200
        deck = response.json()
        assert deck["name"] == "Empty Deck"
        assert len(deck["cards"]) == 0


class TestGetDeck:
    """Test the GET /decks/{deck_id} endpoint."""

    def test_get_existing_deck(self, client, created_deck):
        """Test getting an existing deck by ID."""
        deck_id = created_deck["id"]
        response = client.get(f"/decks/{deck_id}")

        assert response.status_code == 200
        deck = response.json()
        assert deck["id"] == deck_id
        assert deck["name"] == "Spanish Vocabulary"
        assert len(deck["cards"]) == 3

    def test_get_nonexistent_deck(self, client, temp_data_dir):
        """Test getting a deck that doesn't exist."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/decks/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestReplaceDeck:
    """Test the PUT /decks/{deck_id} endpoint."""

    def test_replace_deck_success(self, client, created_deck):
        """Test successfully replacing a deck."""
        deck_id = created_deck["id"]
        update_data = {"name": "New Name", "description": "New Description"}

        response = client.put(f"/decks/{deck_id}", json=update_data)

        assert response.status_code == 200
        deck = response.json()
        assert deck["name"] == "New Name"
        assert deck["description"] == "New Description"
        # Cards should remain unchanged
        assert len(deck["cards"]) == 3

    def test_replace_nonexistent_deck(self, client, temp_data_dir):
        """Test replacing a deck that doesn't exist."""
        fake_id = str(uuid.uuid4())
        update_data = {"name": "New Name", "description": "New Description"}

        response = client.put(f"/decks/{fake_id}", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

class TestUpdateDeck:
    """Test the PATCH /decks/{deck_id} endpoint."""

    def test_update_deck_success(self, client, created_deck):
        """Test successfully updating a deck."""
        deck_id = created_deck["id"]
        update_data = {
            "name": "Updated Spanish Vocabulary",
            "description": "Updated description for Spanish words",
        }

        response = client.patch(f"/decks/{deck_id}", json=update_data)

        assert response.status_code == 200
        deck = response.json()
        assert deck["id"] == deck_id
        assert deck["name"] == update_data["name"]
        assert deck["description"] == update_data["description"]
        # Cards should remain unchanged
        assert len(deck["cards"]) == 3

    def test_update_deck_name_only(self, client, created_deck):
        """Test updating only the deck name."""
        deck_id = created_deck["id"]
        update_data = {"name": "New Name"}

        response = client.patch(f"/decks/{deck_id}", json=update_data)

        assert response.status_code == 200
        deck = response.json()
        assert deck["name"] == "New Name"
        assert deck["description"] == "Basic Spanish words and phrases"

    def test_update_nonexistent_deck(self, client, temp_data_dir):
        """Test updating a deck that doesn't exist."""
        fake_id = str(uuid.uuid4())
        update_data = {"name": "New Name", "description": "New Description"}

        response = client.patch(f"/decks/{fake_id}", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestAddCard:
    """Test the POST /decks/{deck_id}/cards endpoint."""

    def test_add_card_success(self, client, created_deck):
        """Test successfully adding a card to a deck."""
        deck_id = created_deck["id"]
        new_card = {"front": "Good morning", "back": "Buenos días"}

        response = client.post(f"/decks/{deck_id}/cards", json=new_card)

        assert response.status_code == 200
        card = response.json()
        assert "id" in card
        assert card["front"] == new_card["front"]
        assert card["back"] == new_card["back"]

        # Verify the card was added to the deck
        deck_response = client.get(f"/decks/{deck_id}")
        deck = deck_response.json()
        assert len(deck["cards"]) == 4  # Original 3 + 1 new

    def test_add_card_to_nonexistent_deck(self, client, temp_data_dir):
        """Test adding a card to a deck that doesn't exist."""
        fake_id = str(uuid.uuid4())
        new_card = {"front": "Test", "back": "Prueba"}

        response = client.post(f"/decks/{fake_id}/cards", json=new_card)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestDeleteCard:
    """Test the DELETE /decks/{deck_id}/cards/{card_id} endpoint."""

    def test_delete_card_success(self, client, created_deck):
        """Test successfully deleting a card from a deck."""
        deck_id = created_deck["id"]
        card_to_delete = created_deck["cards"][0]  # Delete the first card
        card_id = card_to_delete["id"]

        response = client.delete(f"/decks/{deck_id}/cards/{card_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Card deleted"

        # Verify the card was removed from the deck
        deck_response = client.get(f"/decks/{deck_id}")
        deck = deck_response.json()
        assert len(deck["cards"]) == 2  # Original 3 - 1 deleted

        # Verify the specific card is no longer in the deck
        card_ids = [card["id"] for card in deck["cards"]]
        assert card_id not in card_ids

    def test_delete_card_from_nonexistent_deck(self, client, temp_data_dir):
        """Test deleting a card from a deck that doesn't exist."""
        fake_deck_id = str(uuid.uuid4())
        fake_card_id = str(uuid.uuid4())

        response = client.delete(f"/decks/{fake_deck_id}/cards/{fake_card_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_nonexistent_card(self, client, created_deck):
        """Test deleting a card that doesn't exist from an existing deck."""
        deck_id = created_deck["id"]
        fake_card_id = str(uuid.uuid4())

        response = client.delete(f"/decks/{deck_id}/cards/{fake_card_id}")

        # This should succeed (no error) as the card is simply not found to delete
        assert response.status_code == 200
        assert response.json()["message"] == "Card deleted"

        # Verify all original cards are still there
        deck_response = client.get(f"/decks/{deck_id}")
        deck = deck_response.json()
        assert len(deck["cards"]) == 3  # All original cards remain


class TestEndToEndWorkflow:
    """Test complete workflows using multiple endpoints."""

    def test_complete_deck_lifecycle(self, client, temp_data_dir):
        """Test a complete workflow: create deck, add card, update deck, delete card."""
        # 1. Create a deck
        deck_data = {
            "name": "French Basics",
            "description": "Basic French vocabulary",
            "cards": [
                {"front": "Cat", "back": "Chat"},
                {"front": "Dog", "back": "Chien"},
            ],
        }

        create_response = client.post("/decks/import", json=deck_data)
        assert create_response.status_code == 200
        deck = create_response.json()
        deck_id = deck["id"]

        # 2. Add a new card
        new_card = {"front": "Bird", "back": "Oiseau"}
        add_card_response = client.post(f"/decks/{deck_id}/cards", json=new_card)
        assert add_card_response.status_code == 200

        # 3. Update the deck
        update_data = {
            "name": "French Animals",
            "description": "French vocabulary for animals",
        }
        update_response = client.put(f"/decks/{deck_id}", json=update_data)
        assert update_response.status_code == 200

        # 4. Verify final state
        final_response = client.get(f"/decks/{deck_id}")
        final_deck = final_response.json()

        assert final_deck["name"] == "French Animals"
        assert final_deck["description"] == "French vocabulary for animals"
        assert len(final_deck["cards"]) == 3

        # 5. Delete a card
        card_to_delete_id = final_deck["cards"][0]["id"]
        delete_response = client.delete(f"/decks/{deck_id}/cards/{card_to_delete_id}")
        assert delete_response.status_code == 200

        # 6. Verify final state after deletion
        final_final_response = client.get(f"/decks/{deck_id}")
        final_final_deck = final_final_response.json()
        assert len(final_final_deck["cards"]) == 2
