""" This module contains the QSS styles for the table widget. """

header_bg = "#CCD4F0"  # header background
header_border_color = "#000000"
header_hover_color = "#BEC5DF"
header_font_color = "#22242A"  # header font color
header_font_size = "14pt"  # header font size

CORNER_BTN_STYLE = f"""
    QTableCornerButton::section {{
        background-color: {header_bg};
        }}
"""



HORIZONTAL_HEADER_STYLE = f"""
    QHeaderView::section {{
        background-color: {header_bg};
        color: {header_font_color};
        font-size: {header_font_size};
        font-family: "Calibri";
        border-left: 1px solid {header_border_color};            
        }}
        
    QHeaderView::section:checked {{
        background-color: {header_bg};           
        }}
        
    QHeaderView::section:hover {{
        background-color: {header_hover_color};
        }}
        

"""

VERTICAL_HEADER_STYLE = f"""
    QHeaderView::section:vertical {{
        background-color: {header_bg};
        color: {header_font_color};
        }}
    QHeaderView::section:vertical:hover {{
        background-color: {header_hover_color};
        }}
"""
