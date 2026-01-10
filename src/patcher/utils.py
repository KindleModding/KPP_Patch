import functools
import inspect
import sys
from typing import Protocol, get_type_hints


class PatchFunction(Protocol):
    def __call__(self, khbc: "KindleHBC") -> None: ...


def strip_self(sig: inspect.Signature) -> inspect.Signature:
    params = list(sig.parameters.values())
    if params and params[0].name == "self":
        params = params[1:]
    return sig.replace(parameters=params)


def normalise(t: object) -> object:
    if t is None:
        return type(None)
    if t == "None":
        return type(None)
    return t


def matches_signature(fn, proto: Protocol) -> bool:
    module = sys.modules.get(fn.__module__, {})

    proto_sig = strip_self(inspect.signature(proto.__call__))
    proto_hints = get_type_hints(proto.__call__, globalns=module.__dict__, localns={})

    fn_sig = inspect.signature(fn)
    fn_hints = get_type_hints(fn, globalns=module.__dict__, localns={})

    if list(proto_sig.parameters) != list(fn_sig.parameters):
        return False

    for name, _ in proto_sig.parameters.items():
        if fn_hints.get(name) != proto_hints.get(name):
            return False

    return normalise(fn_hints.get("return")) == normalise(proto_hints.get("return"))


@functools.cache
def current_patches() -> dict[str, PatchFunction]:
    from . import patcher

    return {
        name: obj
        for name, obj in inspect.getmembers(patcher, inspect.isfunction)
        if matches_signature(obj, PatchFunction) and name.startswith("patch_")
    }


def patch_doc(func: PatchFunction) -> str:
    return inspect.getdoc(func) or "Not yet documented"
