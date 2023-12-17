""" This module contains the QSS styles for the table widget. """

background = item_border = "#B3BFDC"

header_bg = "#36436A"  # header background
header_font_color = "#DDEAF3"  # header font color
header_font_size = "14pt"  # header font size


HEADER_STYLE = f"""
QTabelView {{
        background-color: {background};
        }}
    
    QHeaderView::section {{
        background-color: {header_bg};
        color: {header_font_color};
        font-size: {header_font_size};
        font-family: "Calibri";
        border-top: 1px solid #33384F;
        border-right: 3px solid #33384F;
        border-bottom: 1px solid #33384F;
        border-left: 1px solid #33384F;            
    }}


    QTableCornerButton::section {{
        background-color: #36436A;
    }}

"""
