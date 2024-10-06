import tabulate

from functools import partial
from tabulate import _append_multiline_row, _pad_row, _append_basic_row, _append_line, _is_separating_line, \
    _html_begin_table_without_header


# hack: fix tabulate to correctly (?) render separating lines if fmt.linebetweenrows is truthy
def fixed_format_table(fmt, headers, rows, colwidths, colaligns, is_multiline, rowaligns):
    """Produce a plain-text representation of the table."""
    lines = []
    hidden = fmt.with_header_hide if (headers and fmt.with_header_hide) else []
    pad = fmt.padding
    headerrow = fmt.headerrow

    # hack 4
    while rows and _is_separating_line(rows[-1]):
        rows.pop()
        rowaligns.pop()

    padded_widths = [(w + 2 * pad) for w in colwidths]
    if is_multiline:
        pad_row = lambda row, _: row  # noqa do it later, in _append_multiline_row
        append_row = partial(_append_multiline_row, pad=pad)
    else:
        pad_row = lambda row, pad: row if _is_separating_line(row) else _pad_row(row, pad)  # hack 1 here
        append_row = _append_basic_row

    padded_headers = pad_row(headers, pad)
    padded_rows = [pad_row(row, pad) for row in rows]

    if fmt.lineabove and "lineabove" not in hidden:
        _append_line(lines, padded_widths, colaligns, fmt.lineabove)

    if padded_headers:
        append_row(lines, padded_headers, padded_widths, colaligns, headerrow)
        if fmt.linebelowheader and "linebelowheader" not in hidden:
            _append_line(lines, padded_widths, colaligns, fmt.linebelowheader)

    # hack 3 is switching the order here
    separating_line = (
        fmt.linebelowheader
        or fmt.linebetweenrows
        or fmt.linebelow
        or fmt.lineabove
        or tabulate.Line("", "", "", "")
    )
    if padded_rows and fmt.linebetweenrows and "linebetweenrows" not in hidden:
        # initial rows with a line below
        # hack 2 is in here
        for i, row in enumerate(padded_rows[:-1]):
            if _is_separating_line(row):
                continue

            append_row(
                lines, row, padded_widths, colaligns, fmt.datarow
            )

            if _is_separating_line(padded_rows[i + 1]):
                _append_line(lines, padded_widths, colaligns, separating_line)
            else:
                _append_line(lines, padded_widths, colaligns, fmt.linebetweenrows)

        # the last row without a line below
        append_row(
            lines,
            padded_rows[-1],
            padded_widths,
            colaligns,
            fmt.datarow
        )
    else:
        for row in padded_rows:
            # test to see if either the 1st column or the 2nd column (account for showindex) has
            # the SEPARATING_LINE flag
            if _is_separating_line(row):
                _append_line(lines, padded_widths, colaligns, separating_line)
            else:
                append_row(lines, row, padded_widths, colaligns, fmt.datarow)

    if fmt.linebelow and "linebelow" not in hidden:
        _append_line(lines, padded_widths, colaligns, fmt.linebelow)

    if headers or rows:
        output = "\n".join(lines)
        if fmt.lineabove == _html_begin_table_without_header:
            return tabulate.JupyterHTMLStr(output)
        else:
            return output
    else:  # a completely empty table
        return ""


def monkey_patch_tabulate():
    tabulate._format_table = fixed_format_table
