from collections.abc import Sequence
from dataclasses import dataclass

from hbctool.hbc import InstructionDisassembled


@dataclass
class Pattern:
    pattern: list[tuple] | list[InstructionDisassembled]
    replacement: list[tuple] | list[InstructionDisassembled]


def remove_sequences(source: list, patterns: list[list]) -> list:
    i = 0
    out = []

    while i < len(source):
        matched = False

        for p in patterns:
            if not p:
                continue

            if p[0] != source[i]:
                continue

            if p == source[i : i + len(p)]:
                i += len(p)
                matched = True
                break

        if not matched:
            out.append(source[i])
            i += 1

    return out


def replace_sequences(source: list, patterns: Sequence[Pattern]) -> list:
    i = 0
    out = []

    while i < len(source):
        matched = False

        for p in patterns:
            if p.pattern[0] != source[i]:
                continue

            if p.pattern == source[i : i + len(p.pattern)]:
                out += p.replacement
                i += len(p.pattern)
                matched = True
                break

        if not matched:
            out.append(source[i])
            i += 1

    return out
