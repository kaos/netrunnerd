python_sources(
    overrides={
        "main.py": dict(dependencies=["src/netrunner/engine"]),
    },
)

pex_binary(
    name="netrunnerd",
    entry_point="main.py",
)
