import curses

def readChrStr(stdscr):
    curses.curs_set(1)
    stdscr.keypad(True)

    text = ""
    max_length = 30

    while True:
        stdscr.clear()

        stdscr.addstr(2, 2, "Enter your username:")
        stdscr.addstr(4, 2, f"Username: {text}")

        stdscr.addstr(6, 2, "Press Enter to submit.")
        stdscr.addstr(7, 2, "Press Backspace to delete.")

        # Position the cursor after the typed text
        stdscr.move(4, 12 + len(text))
        stdscr.refresh()

        key = stdscr.getch()

        if key in (10, 13, curses.KEY_ENTER):
            break

        elif key in (curses.KEY_BACKSPACE, 127, 8):
            text = text[:-1]

        elif 32 <= key <= 126 and len(text) < max_length:
            text += chr(key)

    stdscr.clear()
    stdscr.addstr(2, 2, f"Username entered: {text}")
    stdscr.addstr(4, 2, "Press any key to exit.")
    stdscr.refresh()
    stdscr.getch()


def readStr(stdscr: curses.window):
    curses.curs_set(1)  # Show the cursor
    curses.echo() # Show the inputted text

    stdscr.addstr(2, 2, "Enter your name: ")
    stdscr.refresh()
    curses.echo()
    # Read user input
    name = stdscr.getstr(2, 20, 30)

    # Convert bytes to a string
    name = name.decode("utf-8")

    stdscr.addstr(4, 2, f"Hello, {name}!")
    stdscr.addstr(6, 2, "Press any key to exit.")

    stdscr.refresh()
    stdscr.getch()


def menu(stdscr: curses.window, options: list[str]):
    """
    Display a scrollable menu using curses.

    Args:
        stdscr: The curses standard screen.
        options: A list of menu options (strings).

    Returns:
        The index of the selected option, or -1 if cancelled.
    """
    if not options:
        return -1

    selected = 0
    scroll_offset = 0

    while True:
        stdscr.erase()

        height, width = stdscr.getmaxyx()

        # Reserve rows for the title, instructions, and footer.
        title_row = 0
        menu_start = 2
        footer_rows = 2
        menu_height = max(1, height - menu_start - footer_rows)

        # Keep the selection visible.
        if selected < scroll_offset:
            scroll_offset = selected
        elif selected >= scroll_offset + menu_height:
            scroll_offset = selected - menu_height + 1

        # Draw title.
        title = " Select an option "
        if width > 1:
            stdscr.addnstr(title_row, 0, title, width - 1,
                           curses.A_BOLD | curses.A_UNDERLINE)

        # Display visible options.
        for row in range(menu_height):
            option_index = scroll_offset + row

            if option_index >= len(options):
                break

            text = options[option_index]

            # Indicate selection.
            if option_index == selected:
                prefix = "> "
                attr = curses.A_REVERSE | curses.A_BOLD
            else:
                prefix = "  "
                attr = curses.A_NORMAL

            # Truncate long options to fit the terminal.
            available_width = max(0, width - len(prefix) - 1)
            display_text = prefix + text[:available_width]

            try:
                stdscr.addnstr(
                    menu_start + row,
                    0,
                    display_text,
                    max(0, width - 1),
                    attr
                )
            except curses.error:
                # Avoid crashes on terminals with limited dimensions.
                pass

        # Draw scrollbar when scrolling is necessary.
        if len(options) > menu_height and width >= 3:
            scrollbar_x = width - 2
            track_height = menu_height

            try:
                stdscr.addch(menu_start, scrollbar_x, curses.ACS_UARROW)
                stdscr.addch(
                    menu_start + track_height - 1,
                    scrollbar_x,
                    curses.ACS_DARROW
                )

                if track_height > 2:
                    thumb_track = track_height - 2

                    thumb_position = int(
                        (scroll_offset / max(1, len(options) - menu_height))
                        * max(0, thumb_track - 1)
                    )

                    for i in range(thumb_track):
                        char = (
                            curses.ACS_CKBOARD
                            if i == thumb_position
                            else curses.ACS_VLINE
                        )

                        stdscr.addch(
                            menu_start + 1 + i,
                            scrollbar_x,
                            char
                        )
            except curses.error:
                pass

        # Footer and navigation instructions.
        footer_y = height - 2

        if footer_y >= 0 and width > 1:
            instructions = (
                "Up/Down: Navigate | PgUp/PgDn: Page | "
                "Home/End: Jump | Enter: Select | q: Quit"
            )

            try:
                stdscr.addnstr(
                    footer_y,
                    0,
                    instructions,
                    width - 1,
                    curses.A_DIM
                )

                status = (
                    f"Option {selected + 1}/{len(options)}"
                    f" | Visible {scroll_offset + 1}-"
                    f"{min(scroll_offset + menu_height, len(options))}"
                )

                stdscr.addnstr(
                    height - 1,
                    0,
                    status,
                    width - 1,
                    curses.A_BOLD
                )
            except curses.error:
                pass

        stdscr.refresh()

        # Read keyboard input.
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected = max(0, selected - 1)

        elif key == curses.KEY_DOWN:
            selected = min(len(options) - 1, selected + 1)

        elif key == curses.KEY_PPAGE:  # Page Up
            selected = max(0, selected - menu_height)

        elif key == curses.KEY_NPAGE:  # Page Down
            selected = min(len(options) - 1, selected + menu_height)

        elif key == curses.KEY_HOME:
            selected = 0

        elif key == curses.KEY_END:
            selected = len(options) - 1

        elif key in (curses.KEY_ENTER, 10, 13):
            return selected

        elif key in (ord("q"), ord("Q"), 27):  # q or Escape
            return -1
