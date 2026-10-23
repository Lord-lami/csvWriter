import csv, curses


fields = []

def fillFields(stdscr: curses.window):
    stdscr.clear()
    curses.curs_set(1)  # Show the cursor
    curses.echo() # Show the inputted text

    stdscr.scrollok(True)
    stdscr.idlok(True)

    stdscr.addstr(2, 2, "What fields do you want to record")
    field_name = "place holder"
    while field_name:
        field_nbr = len(fields) + 1
        field_tag = f"Field {field_nbr}: "
        # eraser = " " * len(fields[-1]) if len(fields) > 0 else ""
        stdscr.addstr(4, 2, "Fields: " + ", ".join(fields))
        stdscr.addstr(3, 2, field_tag)
        stdscr.clrtoeol()
        stdscr.refresh()
        # Read user input
        field_name = stdscr.getstr(3, 2 + len(field_tag), 30)

        # Convert bytes to a string
        field_name = field_name.decode("utf-8")
        if field_name:
            fields.append(field_name + field_constraints[0])

def valueToType(value: str, val_type: str) -> str|int|float|None:
    if val_type == "(Int)":
        try:
            return int(value)
        except ValueError:
            return None
    elif val_type == "(Flt)":
        try:
            actual_value = float(value)
            return value
        except:
            return None
    else:
        return value

def inlineGetValue(stdscr: curses.window, key: int, y: int, x: int, prompt: str, value, val_type: str):
    curses.curs_set(1)
    stdscr.keypad(True)

    new_value = value
    max_length = 30
    valueStr = str(value)
    stdscr.addstr(y, x, f"{prompt}: {valueStr}")

    # Position the cursor after the typed text
    stdscr.move(y, x + len(prompt) + 2 + len(valueStr))
    stdscr.refresh()

    key
    
    if key in (curses.KEY_BACKSPACE, 127, 8):
        valueStr = valueStr[:-1]

    elif type(key) == str and key.isprintable() and len(valueStr) < max_length:
        if valueStr == "0":
            valueStr = ""
        valueStr += key

    new_value = valueToType(valueStr, val_type)
    if new_value == None:
        valueStr = valueStr[:-1]
        new_value = value
    stdscr.clrtoeol()
    
    return new_value

def getValue(stdscr: curses.window, 
                title: str = "", 
                prompt: str = "",
                val_type = "(Str)") -> str|int|float:
    stdscr.clear()
    curses.curs_set(1)  # Show the cursor
    curses.echo() # Show the inputted text

    stdscr.addstr(2, 2, title)
    while True:
        stdscr.addstr(3, 2, prompt)
        stdscr.clrtoeol()
        stdscr.refresh()
        curses.echo()
        # Read user input
        new_value_str = stdscr.getstr(3, len(prompt) + 2, 30)

        # Convert bytes to a string
        new_value_str = new_value_str.decode("utf-8")

        new_value = valueToType(new_value_str, val_type)

        if new_value == None:
            stdscr.addstr(3, 2, f"Invalid {val_type}: {new_value_str}. Try Again")
            stdscr.clrtoeol()
            stdscr.refresh()
            stdscr.getch()
            continue
        else:
            return new_value

def menu(stdscr: curses.window, options: list[str], 
               action: function[curses.window, int, int],
               serial_list: list[str] = None,
                title: str = "Select an option",
                instructions: str = "Up/Down: Navigate | PgUp/PgDn: Page | "
                                    "Home/End: Jump | q: Quit"):
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
        footer_rows = instructions.count("\n") + 2
        menu_height = max(1, height - menu_start - footer_rows)

        # Keep the selection visible.
        if selected < scroll_offset:
            scroll_offset = selected
        elif selected >= scroll_offset + menu_height:
            scroll_offset = selected - menu_height + 1

        # Draw title.
        if width > 1:
            stdscr.addnstr(title_row, 0, title, width - 1,
                           curses.A_BOLD | curses.A_UNDERLINE)

        # Display visible options.
        for row in range(menu_height):
            option_index = scroll_offset + row

            if option_index >= len(options):
                break

            prefix = ""
            if serial_list and len(serial_list) == len(options):
                prefix = f"{serial_list[option_index]}: "

            text = f"{prefix}{options[option_index]}"

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
        footer_y = height - footer_rows

        if footer_y >= 0 and width > 1:
            # Try to show the instructions and status ignoring 
            # terminal width errors.
            try:
                stdscr.addstr(
                    footer_y,
                    0,
                    instructions,
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
        key = stdscr.get_wch()

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

        elif key in (curses.KEY_ENTER, '\r', '\n', "\r\n"): # Enter to continue
            return True

        elif key == '\x1b':  # Escape
            return False
        y = menu_start + selected
        x = 2

        action(stdscr, key, selected, y, x, options)

field_constraints = ["(Str)", "(Int)", "(Flt)"]

def edit_field_names_and_field_constraints(stdscr: curses.window, key: int, selected: int, *misc):
    constraint_idx = field_constraints.index(fields[selected][-5:])
    if key == curses.KEY_LEFT:
        constraint_idx -= 1
        constraint_idx %= len(field_constraints)
        fields[selected] = fields[selected][:-5] + field_constraints[constraint_idx]

    elif key == curses.KEY_RIGHT:
        constraint_idx += 1
        constraint_idx %= len(field_constraints)
        fields[selected] = fields[selected][:-5] + field_constraints[constraint_idx]
    
    elif key == curses.KEY_DC: # del to delete the field
        del fields[selected]

    elif key == curses.KEY_IC: # ins to insert a field
        new_field_name = getValue(stdscr, "Add New Field", "Field Name: ")
        if new_field_name:
            fields.insert(selected, new_field_name + field_constraints[0])

    elif key in (ord('e'), ord('E')): # e to edit the field name
        constraint = fields[selected][-5:]
        new_field_name =  getValue(stdscr, 
                                    "Edit Field Name", 
                                    f"Changing from {fields[selected][:-5]} to ")
        if new_field_name:
            fields[selected] += new_field_name + constraint

records = []

def collect_record(stdscr: curses.window, key: int, selected: int, *misc):
    y = misc[0]
    x = misc[1]
    record = misc[2]
    record[selected] = inlineGetValue(stdscr, key, y, x, 
                                          fields[selected], 
                                          record[selected],
                                          fields[selected][-5:])

def write_lists_to_csv(filename: str, rows: list[list[object]]) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def mainmenu(stdscr: curses.window):
    # Configure the terminal
    curses.curs_set(0)       # Hide the cursor
    stdscr.keypad(True)      # Enable arrow key handling

    options = [
        "New File",
        "Exit"
    ]

    selected = 0
    message = ""
    while True:
        # Clear the screen before redrawing
        stdscr.clear()

        # Display a title
        stdscr.addstr(2, 4, "=== CSV Writer ===")
        stdscr.addstr(3, 4, message)

        # Display the menu options
        for i, option in enumerate(options):
            y = 4 + i
            x = 6

            if i == selected:
                # Highlight the selected option
                stdscr.addstr(
                    y, x, f"> {option}",
                    curses.A_REVERSE
                )
            else:
                stdscr.addstr(y, x, f"  {option}")

        stdscr.addstr(
            10, 4,
            "Use UP/DOWN to navigate, ENTER to select, ESC to exit."
        )

        stdscr.refresh()

        # Read a keypress
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)

        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)

        elif key in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            if options[selected] == "New File":
                fillFields(stdscr)
                global fields
                proceed = menu(stdscr, fields, edit_field_names_and_field_constraints, 
                           title="Edit the fields",
                           instructions="Up/Down: Navigate | PgUp/PgDn: Page | "
                            "Home/End: Jump | Enter: Continue | Esc: Quit |\n"
                            "Left/Right: Toggle field_Constraints (Str)/(Int)/(Flt) | "
                            "e: Edit Field Name | Delete: Delete Field | "
                            "Insert: Insert New Field |")
                if proceed == False:
                    fields = []
                    continue
                global records
                while True:
                    record = []
                    for f in fields:
                        if f[-5:] == "(Int)":
                            record.append(0)
                        elif f[-5:] == "(Flt)":
                            record.append(0.0)
                        else:
                            record.append("")
                    empty_record = record
                    proceed = menu(stdscr, record, collect_record,
                        serial_list=fields,
                        title="Add a record",
                        instructions="Up/Down: Navigate | PgUp/PgDn: Page | "
                            "Home/End: Jump | Enter: Continue | Esc: Quit |")
                    if proceed == True:
                        records.append(record)
                        continue
                    else:
                        if record != empty_record:
                            records.append(record)
                        message = f"Saved {len(records)} records to output.csv"
                        break

                write_lists_to_csv("output.csv", [fields, *records])

                fields = []
                records = []

            elif options[selected] == "Exit":
                break

        elif key == 27:  # ESC
            break




if __name__ == "__main__":
    print("You could have just downloaded Excel or Libre Office.")
    print("But you had to make me suffer")
    print("Goodbye from CSV Writer")
    print("By Olamide Ifarajimi")
    curses.wrapper(mainmenu)
