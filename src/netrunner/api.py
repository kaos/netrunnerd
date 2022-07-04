import capnp  # noqa

from netrunner import api_capnp as schema  # type: ignore[attr-defined]

# TODO: compile the api.capnp schema
#  $ capnpc -ocython
#  $ capnpc -oc++
#  $ python setup_capnp.py build_ext
#
# Requires: cython


# Assign all top-level schema types here, to keep all type hint violations in one place, as mypy
# doesn't know about or api.capnp schema. (resolved by above TODO)
NetrunnerLobby = schema.NetrunnerLobby
ClientInfo = schema.ClientInfo
Player = schema.Player
Runner = schema.Runner
Corp = schema.Corp
Spectator = schema.Spectator
GameSubscriber = schema.GameSubscriber
Role = schema.Role
Game = schema.Game
Card = schema.Card
