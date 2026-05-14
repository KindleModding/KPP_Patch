import curses

from .hints import PatchFunction, stable_patches, patch_doc


def _menu(stdscr: curses.window, options: list[str]) -> dict[str, bool]:
    if not options:
        return {}

    curses.curs_set(0)
    selected = [False] * len(options)
    index = 0

    while True:
        stdscr.clear()

        stdscr.addstr("Select options (Space to toggle, Enter to confirm)\n\n")

        for i, opt in enumerate(options):
            prefix = "[x] " if selected[i] else "[ ] "
            if i == index:
                stdscr.addstr(prefix + opt + "\n", curses.A_REVERSE)
            else:
                stdscr.addstr(prefix + opt + "\n")

        key = stdscr.getch()

        if key == curses.KEY_UP:
            index = (index - 1) % len(options)
        elif key == curses.KEY_DOWN:
            index = (index + 1) % len(options)
        elif key == ord(" "):
            selected[index] = not selected[index]
        elif key == ord("\n"):
            break

    return dict(zip(options, selected))


def select_patches() -> dict[str, PatchFunction]:
    patches = stable_patches()
    result = curses.wrapper(
        _menu,
        options=list(patches.keys()),
    )

    return {k: v for k, v in patches.items() if result.get(k, False)}
