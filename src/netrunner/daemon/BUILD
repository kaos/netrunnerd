python_sources(
    overrides={
        "lobby.py": dict(dependencies=["src/netrunner/api.capnp:capnp"]),
    },
)

pex_binary(
    name="netrunnerd",
    entry_point="main.py",
)
