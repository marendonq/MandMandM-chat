import os
import importlib
from types import ModuleType
from typing import Iterator


class Handlers:
    ignored = ('__init__.py', '__pycache__')

    @classmethod
    def _handlers_dir(cls) -> str:
        return os.path.dirname(os.path.abspath(__file__))

    @classmethod
    def _all_module_names(cls) -> list:
        return [
            f[:-3] for f in os.listdir(cls._handlers_dir())
            if f.endswith('.py') and f not in cls.ignored
        ]

    @classmethod
    def _module_namespace(cls, handler_name: str) -> str:
        return f'app.infrastructure.handlers.{handler_name}'

    @classmethod
    def iterator(cls) -> Iterator[ModuleType]:
        for name in cls._all_module_names():
            yield importlib.import_module(cls._module_namespace(name))

    @classmethod
    def modules(cls):
        return map(cls._module_namespace, cls._all_module_names())
