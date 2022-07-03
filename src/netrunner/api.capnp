@0xa3e5a1a9902e7f67;

interface NetrunnerLobby {
  myself @0 () -> (info :ClientInfo);
  listGames @1 (page :UInt32 = 1, pageSize :UInt32 = 25) -> (games :List(Game), totalCount :UInt32);
  newGame @2 (role :Role) -> (player :Player);
}

interface ClientInfo {
  getNick @0 () -> (nick :Text);
  setNick @1 (nick :Text);
}

enum Role {
  corp @0;
  runner @1;
}

interface Game {
  getPlayers @0 () -> (corp_nick :Text, runner_nick :Text);
}

interface Player {
  getInfo @0 () -> (nick :Text, role :Role);
  getGame @1 () -> (game :Game);
  # setDeck
  # ...
}
