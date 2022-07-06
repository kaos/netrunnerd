@0xa3e5a1a9902e7f67;

interface NetrunnerLobby {
  myself @0 () -> (info :ClientInfo);
  listGames @1 (page :UInt32 = 1, pageSize :UInt32 = 25) -> (games :List(Game), totalCount :UInt32);
  newGame @2 (role :Role) -> (player :Player);
  joinGame @3 (role :Role, gameId :Game.Id) -> (player :Player);

  listDecks @4 (decklist :Text) -> (decks :List(Deck));
  viewCard @5 (cardCode :Text) -> (card :Card);
}

interface ClientInfo {
  getNick @0 () -> (nick :Text);
  setNick @1 (nick :Text, password :Text = "");
  registerNick @2 (password :Text);
  useDeck @3 (deck :Deck);
}

interface Player {
  getInfo @0 () -> (nick :Text, role :Role);
  getGame @1 () -> (game :Game);
  subscribe @2 (client :GameSubscriber);
}

interface Runner extends(Player) {
}

interface Corp extends(Player) {
}

interface Spectator extends(Player) {
}

interface GameSubscriber {
  # ...
}

enum Role {
  corp @0;
  runner @1;
  spectator @2;
}

struct Game {
  id @0 :Id;
  corp @1 :Participant;
  runner @2 :Participant;
  spectators @3 :List(Text);

  struct Id {
    seq @0 :UInt64;
    pool @1 :Text;
  }

  struct Participant {
    nickName @0 :Text;
    deck @1 :Deck;
    cards @2 :List(CardState);
  }

  struct CardState {
    active @0 :Bool;
    card @1 :Card;
    zone @2 :GameZone;
  }

  enum GameZone {
    deck @0;
    hand @1;
    discard @2;
    scoreArea @3;
    playArea @4;
    bank @5;
    setAside @6;
    removedFromGame @7;
  }
}

struct Deck {
  id @0 :Text;
  name @1 :Text;
  identity @2 :Card;
  cards @3 :List(DeckCard);

  struct DeckCard {
    card @0 :Card;
    count @1 :UInt8;
  }
}

struct Card {
  id @0 :Text;
  code @1 :Text;
  name @2 :Text;
  faction @3 :Faction;
  influence @4 :UInt8;
  unique @5 :Bool;
  deckLimit @6 :UInt8;

  union {
    agenda :group {
      advancementCost @7 :UInt8;
      agendaPoints @8 :UInt8;
    }
    asset :group {
      cost @9 :UInt8;
      strippedText @10 :Text;
      text @11 :Text;
      trashCost @12 :UInt8;
    }
    event :group {
      cost @13 :UInt8;
      strippedText @14 :Text;
      text @15 :Text;
    }
    hardware :group {
      cost @16 :UInt8;
      strippedText @17 :Text;
      text @18 :Text;
    }
    ice :group {
      cost @19 :UInt8;
      keywords @20 :Text;
      strength @21 :UInt8;
      strippedText @22 :Text;
      text @23 :Text;
    }
    identity :group {
      influenceLimit @24 :UInt8;
      keywords @25 :Text;
      minimumDeckSize @26 :UInt8;
    }
    operation :group {
      cost @27 :UInt8;
      strippedText @28 :Text;
      text @29 :Text;
    }
    program :group {
      cost @30 :UInt8;
      keywords @41 :Text;
      memoryCost @31 :UInt8;
      strippedText @32 :Text;
      text @33 :Text;
    }
    resource :group {
      cost @34 :UInt8;
      strippedText @35 :Text;
      text @36 :Text;
    }
    upgrade :group {
      cost @37 :UInt8;
      strippedText @38 :Text;
      text @39 :Text;
      trashCost @40 :UInt8;
    }
  }

  struct Faction {
    side @0 :Side;
    name @1 :Text;

    enum Side {
      corp @0;
      runner @1;
    }
  }
}
