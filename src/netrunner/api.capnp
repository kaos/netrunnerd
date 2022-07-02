@0xa3e5a1a9902e7f67;

interface NetrunnerLobby {
  myself @0 () -> (info :ClientInfo);
}

interface ClientInfo {
  getNick @0 () -> (nick :Text);
  setNick @1 (nick :Text);
}
