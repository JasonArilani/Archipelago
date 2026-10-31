"""Register a self-contained client in the Archipelago Launcher."""
from worlds.LauncherComponents import Component, Type, components, launch


def start_mtiaa_client(*args: str) -> None:
    from .client import run_client
    launch(run_client, name="My Teacher Is an Alien Client", args=args)


components.append(Component(
    "My Teacher Is an Alien Client",
    func=start_mtiaa_client,
    game_name="My Teacher Is an Alien",
    component_type=Type.CLIENT,
))
