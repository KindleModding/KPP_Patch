from hbctool.hbc.hbcbase import InstructionArgumentDisassembled, InstructionDisassembled


def _bare_to_typed(
    source: list[tuple[str, list[tuple[str, bool, int]]]],
) -> list[InstructionDisassembled]:
    out = []
    for x in source:
        arguments = [InstructionArgumentDisassembled._make(a) for a in x[1]]
        out.append(InstructionDisassembled(instruction=x[0], arguments=arguments))
    return out


ALWAYS_TRUE = _bare_to_typed(
    [("LoadConstTrue", [("Reg8", False, 0)]), ("Ret", [("Reg8", False, 0)])]
)
ALWAYS_FALSE = _bare_to_typed(
    [("LoadConstFalse", [("Reg8", False, 0)]), ("Ret", [("Reg8", False, 0)])]
)
ALWAYS_UNDEFINED = _bare_to_typed(
    [
        ("LoadConstUndefined", [("Reg8", False, 0)]),
        ("Ret", [("Reg8", False, 0)]),
    ]
)
EMPTY_OBJECT = _bare_to_typed(
    [("NewObject", [("Reg8", False, 0)]), ("Ret", [("Reg8", False, 0)])]
)
