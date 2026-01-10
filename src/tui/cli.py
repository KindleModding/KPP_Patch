import argparse
from pathlib import Path

from src.patcher.utils import current_patches, patch_doc


def filetype(value: str) -> Path:
    try:
        file = Path(value)
        if not file.exists():
            raise ValueError("File doesn't exist")
        return file
    except Exception as e:
        raise ValueError("Invalid value") from e


def form_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kpp_patcher",
        description="Patch different behaviours of the Kindle KPP app",
    )

    parser.add_argument(
        "filename",
        type=filetype,
        help="Path to the KPPMainApp.js.hbc file",
    )

    parser.add_argument(
        "--interactive",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Use interactive mode to select patches. If this option is set, cli "
            "choices are ignored. Disable with --no-interactive."
        ),
    )

    patches = current_patches()

    for name, patch in patches.items():
        parser.add_argument(
            f"--{name}",
            action="store_true",
            default=False,
            help=patch_doc(patch),
        )

    return parser


def parse_cli() -> tuple[argparse.Namespace, "dict[str, PatchFunction]"]:
    parser = form_parser()

    args = parser.parse_args()

    patches = current_patches()
    selected_patches = {k: v for k, v in patches.items() if getattr(args, k, False)}

    return args, selected_patches
