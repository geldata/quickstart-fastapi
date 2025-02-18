module default {
  type Card {
    required order: int64;
    required front: str;
    required back: str;
  };
    
  type Deck {
    required name: str;
    description: str;
    multi cards: Card {
      constraint exclusive;
      on target delete allow;
    };
  };
}
