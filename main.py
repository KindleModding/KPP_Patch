import logging

from src.patcher import KindleHBC
from src.tui.cli import parse_cli

try:
    import curses as _curses

    from src.tui.interactive import select_patches
except ImportError:
    _HAS_CURSES = False
else:
    _HAS_CURSES = True


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    logger.info("KPP_Patch running!")

    args, selected_patches = parse_cli()

    if args.interactive and _HAS_CURSES:
        selected_patches = select_patches()

    if not selected_patches:
        raise SystemExit("Select at least one patch. Nothing done. Exiting...")

    khbc = KindleHBC(args.filename)

    for patch_name, patch in selected_patches.items():
        logger.info("Applying patch %s...", patch_name)
        patch(khbc)

    patchf = args.filename.with_name(f"{args.filename.name}.patched")
    khbc.dump(patchf)


if __name__ == "__main__":
    main()
