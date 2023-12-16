""" This module contains the QSS styles for the table widget. """

app_accent_color = "#36436A"

background = item_border = "#B3BFDC"  # below rows, item borders

item_bg = "#595D6E"  # item background

item_font_color = "#DDEAF3"  # item font color
item_font_hover_color = "#DDEAF3"  # item font color when hovered
item_font_selected_color = "#232323"  # item font color when selected

item_hover_bg = app_accent_color  # item background when hovered

item_border_left = item_border_top = "#30494D"  # item border left
item_hover_border = "#646879"  # item border when hovered
item_selected_bg = "#DCFFFF"  # item background when selected
item_selected_border = app_accent_color  # item border when selected

header_bg = "#36436A"  # header background
header_font_color = "#DDEAF3"  # header font color
header_font_size = "14pt"  # header font size
table_font_size = "8pt"  # table font size
selected_font_size = "15pt"  # selected item font size


TABLE_STYLES = f"""
    QTableView {{
        background-color: {background};
        gridline-color: transparent;
    }}

    QTableView::item {{
    }}

    QTableView::item:hover {{
    }}
    
    QTableView::item:selected {{
        }}
    
    QTableView::item:focus {{
        outline: none;
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
