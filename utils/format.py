def adjust_code_formatting(code: str):
    lines = code.splitlines()
    adjusted_lines = []
    add_empty_line_next = False

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        if stripped_line == '}':
            adjusted_lines.append(line)
            add_empty_line_next = True
        else:
            if add_empty_line_next:
                adjusted_lines.append('')  # Ensure exactly one empty line
                add_empty_line_next = False
            if stripped_line or (adjusted_lines and adjusted_lines[-1] != ''):
                adjusted_lines.append(line)

    return '\n'.join(adjusted_lines)