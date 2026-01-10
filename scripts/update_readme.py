#!/usr/bin/env python

from src.patcher.utils import current_patches, patch_doc
from src.tui.cli import form_parser


def update_help():
    TAG_START = "<!--CH0-->\n"
    TAG_END = "<!--CH1-->\n"

    parser = form_parser()

    processed = []

    with open("README.md", "r", encoding="utf-8") as readme:
        in_replace = False

        for line in readme:
            if line == TAG_START:
                in_replace = True
                processed.append(line)
                processed.append("```\n")
                processed.append(parser.format_help())
                processed.append("```\n")
                continue

            if line == TAG_END:
                in_replace = False
                processed.append(line)
                continue

            if in_replace:
                continue

            processed.append(line)

    with open("README.md", "w", encoding="utf-8") as readme:
        readme.write("".join(processed))


def document_patch(func) -> str:
    doc = patch_doc(func)

    result = []

    result.append(f"### {func.__name__}")
    result.append("")

    for line in doc.splitlines():
        if "docs/" in line:
            split = line.split(" ")
            for elem in split:
                if elem.startswith("docs/"):
                    result.append(f"![]({elem})")
            continue

        result.append(line)

    result.append("\n\n")

    return "\n".join(result)


def update_patches():
    TAG_START = "<!--CP0-->\n"
    TAG_END = "<!--CP1-->\n"

    processed = []

    patches = current_patches()

    with open("README.md", "r", encoding="utf-8") as readme:
        in_replace = False

        for line in readme:
            if line == TAG_START:
                in_replace = True
                processed.append(line)
                for patch in patches.values():
                    processed.append(document_patch(patch))
                continue

            if line == TAG_END:
                in_replace = False
                processed.append(line)
                continue

            if in_replace:
                continue

            processed.append(line)

    with open("README.md", "w", encoding="utf-8") as readme:
        readme.write("".join(processed))


if __name__ == "__main__":
    update_help()
    update_patches()
