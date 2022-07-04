@0xa3e5a1a9902e7f67;

interface NetrunnerLobby {
  myself @0 () -> (info :ClientInfo);
  listGames @1 (page :UInt32 = 1, pageSize :UInt32 = 25) -> (games :List(Game), totalCount :UInt32);
  newGame @2 (role :Role) -> (player :Player);
  joinGame @3 (role :Role, gameId :Game.Id) -> (player :Player);

  listDecks @4 (decklist :Text) -> (decks :List(Deck));
}

interface ClientInfo {
  getNick @0 () -> (nick :Text);
  setNick @1 (nick :Text, password :Text = "");
  registerNick @2 (password :Text);
  selectDeck @3 (deck :Deck);
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
  cards @2 :List(DeckCard);

  struct DeckCard {
    card @0 :Card;
    count @1 :UInt8;
  }
}

struct Card {
  id @0 :UInt32;
  name @1 :Text;
  faction @2 :Faction;
  influence :union {
    none @3 :Void;
    value @4 :UInt8;
  }

  union {
    identity :group {
      minimumDeckSize @5 :UInt8;
      influenceLimit @6 :UInt8;
    }
    agenda :group {
      dummy @7 :Void;
    }
    # asset :group {}
    # ice :group {}
    # operation :group {}
    # upgrade :group {}
    # event :group {}
    # hardware :group {}
    # program :group {}
    # resource :group {}
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
