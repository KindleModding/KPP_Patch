import pytest

from src.utils.collections import remove_sequences


def test_remove_sequences():
    patterns = [
        [
            ("LoadConstString", [("Reg8", False, 1), ("UInt16", True, 11289)]),
            (
                "PutById",
                [
                    ("Reg8", False, 4),
                    ("Reg8", False, 1),
                    ("UInt8", False, 16),
                    ("UInt16", True, 11289),
                ],
            ),
        ],
        [
            (
                "PutOwnByIndex",
                [("Reg8", False, 5), ("Reg8", False, 1), ("UInt8", False, 1)],
            ),
        ],
    ]

    source = [
        ("LoadConstString", [("Reg8", False, 1), ("UInt16", True, 9099)]),
        (
            "PutById",
            [
                ("Reg8", False, 4),
                ("Reg8", False, 1),
                ("UInt8", False, 15),
                ("UInt16", True, 9099),
            ],
        ),
        ("LoadConstString", [("Reg8", False, 1), ("UInt16", True, 11289)]),
        (
            "PutById",
            [
                ("Reg8", False, 4),
                ("Reg8", False, 1),
                ("UInt8", False, 16),
                ("UInt16", True, 11289),
            ],
        ),
        ("Jmp", [("Addr8", False, 13)]),
        ("LoadConstInt", [("Reg8", False, 8), ("Imm32", False, 365)]),
        (
            "Call2",
            [
                ("Reg8", False, 1),
                ("Reg8", False, 10),
                ("Reg8", False, 11),
                ("Reg8", False, 8),
            ],
        ),
        (
            "PutOwnByIndex",
            [("Reg8", False, 5), ("Reg8", False, 1), ("UInt8", False, 1)],
        ),
    ]

    result = remove_sequences(source, patterns)

    assert result == source[:2] + source[4:-1]
