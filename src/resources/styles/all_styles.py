main_color = '#212121'
opacity = 0.50
title_bar_color = main_color
title_bar_border_color = "#CCD4F0"

MAIN_WINDOW_STYLE = f"""
    QMainWindow{{
    background-color: {main_color};
    border-top: 2px solid {title_bar_border_color};
    border-left: 2px solid {title_bar_border_color};

    }}
"""

TITLE_BAR = f"""
#containerWidget {{
    background-color: {title_bar_color};
    color: white;
    }}
    
QLabel#labelCustomTitle {{
    color: white;
    margin-left: 8px;
    }}
    
QPushButton {{
    background-color: {title_bar_color};
    padding: 10px 10px;
    border-top: 0px solid #6E76B2;
    border-bottom: 0px solid #6E76B2;
    }}

QPushButton:hover {{
    background-color: #393939;
    border-bottom: 0px solid #6E76B2;
    }}

QPushButton:pressed {{
    background-color: {title_bar_color};
    border-bottom: 4px solid #6E76B2;
    }}

QPushButton#closeTitleButton {{
    background-color: {title_bar_color};
    padding: 10px 10px;
    border-top: 0px solid #6E76B2;
    border-bottom: 0px solid #6E76B2;
    }}

QPushButton#closeTitleButton:hover {{
    background-color: #c42b1c;
    border-bottom: 0px solid #6E76B2;
    }}

QPushButton#closeTitleButton:pressed {{
    background-color: {title_bar_color};
    border-bottom: 4px solid #6E76B2;
    }}


"""

SIDEBAR = f"""
QWidget#Sidebar {{
        background-color: {title_bar_color};
        border-left: 2px solid {title_bar_border_color};

}}
"""

SIDEBAR_BTN_COLOR = "#36436A"
SIDEBAR_BTN_COLOR_HOVER = "#101020"

LEFT_SIDE_BUTTONS_PRIMARY = f"""
    QPushButton {{
        background-color: {SIDEBAR_BTN_COLOR};
        color: white;
        font: 10pt "Nunito Sans";
        text-align: left; 
        padding: 5px 0px 5px 8px;
        border: none;
    }}

    QPushButton:hover {{
        background-color: {SIDEBAR_BTN_COLOR_HOVER};
        color: white;
        margin-top: 1px;
        margin-left: 1px;
        border-right: 1px solid #6E76B2;
        border-bottom: 1px solid #6E76B2;
        }}

    QPushButton:pressed {{
        background-color: #5394DD;
        color: #FFFFFF;
    }}
"""

LEFT_SIDE_BUTTONS_SECONDARY = LEFT_SIDE_BUTTONS_PRIMARY

# THIS IS NOT IN USE, BUT IF I WANT, I CAN SET DIFFERENT STYLES FOR PRIMARY AND SECONDARY BUTTONS
# FOR NOW, THEY BOTH GET THE SAME STYLESHEET
