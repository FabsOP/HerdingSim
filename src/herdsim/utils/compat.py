"""Loads .terrain files saved before the modules moved into the herdsim package."""
import pickle


MODULE_ALIASES = {
    "terrain": "herdsim.core.terrain",
    "boid": "herdsim.core.boid",
    "flock": "herdsim.core.flock",
    "vector": "herdsim.core.vector",
    "path_utils": "herdsim.utils.path_utils",
}


class _Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module in MODULE_ALIASES:
            module = MODULE_ALIASES[module]
        elif module.startswith("widgets."):
            module = "herdsim.ui." + module.split(".", 1)[1]
        return super().find_class(module, name)


def load(fileobj):
    return _Unpickler(fileobj).load()
