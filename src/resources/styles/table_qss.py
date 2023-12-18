""" This module contains the QSS styles for the table widget. """

background = item_border = "#B3BFDC"

header_bg = "#36436A"  # header background
header_font_color = "#DDEAF3"  # header font color
header_font_size = "14pt"  # header font size

TABLE_STYLE = f"""
    QTableCornerButton::section {{
        background-color: {header_bg};
        }}
"""

HORIZONTAL_HEADER_STYLE = f"""
    QHeaderView::section:horizontal {{
        background-color: {header_bg};
        color: {header_font_color};
        font-size: {header_font_size};
        font-family: "Calibri";
        border-top: 1px solid #33384F;
        border-right: 3px solid #33384F;
        border-bottom: 1px solid #33384F;
        border-left: 1px solid #33384F;            
        }}
    QHeaderView::section:horizontal:hover {{
        background-color: blue;
        }}
"""

VERTICAL_HEADER_STYLE = f"""
    QHeaderView::section:vertical {{
        background-color: {header_bg};
        color: {header_font_color};
        }}
    QHeaderView::section:vertical:hover {{
        background-color: blue;
        }}
"""
