main_color = '#212121'

MAIN_WINDOW_STYLE = f"""
    QMainWindow{{
    background-color: {main_color};
    border-top: 2px solid #575757;
    border-bottom: 2px solid #575757;
    }}
"""

title_bar_color = main_color

HEADERS_STYLE = "background-color: red;"







TITLE_BAR = f"""
#containerWidget {{
    background-color: {title_bar_color};
    border-top: 2px solid #575757;
    color: white;
    }}
    
QLabel#labelCustomTitle {{
    color: white;
    }}
    
QPushButton {{
    background-color: {title_bar_color};
    color: white;
    padding: 10px 10px;
    border: none;
    }}

QPushButton:hover {{
    background-color: #282828;
    color: white;
    padding: 9px 9px;
    margin-top: 1px;
    margin-left: 1px;
    border-right: 1px solid #6E76B2;
    border-bottom: 1px solid #6E76B2;

    }}

QPushButton:pressed {{
    background-color: {title_bar_color};
    color: white;
    padding: 10px 10px;
    border: none;
    }}

"""

CUSTOM_TABLE_VIEW = """
    QTableView {
        background-color: {bg_color};
        outline: 0;
        font: {font_size}pt;
        color: #03104E;
        alternate-background-color: {alt_bg_color};
        gridline-color: #EEEEEE;
    }
"""

TABLE_VIEW = """
    QTableView {{
        Background-color: {bg_color};
        outline: 0;
        font: {font_size}pt;
        color: #03104E;
        alternate-background-color: {alt_bg_color};
        gridline-color: {bg_color};
    }}
    QTableView::item {{
        border-bottom: 1px solid #C8DBF2;
        padding-left: 20px;
        padding-right: 20px;
    }}
    
    QTableCornerButton::section {{
        background-color: #A2A2A2;
        border: 1px solid #B1B8BB;
    }}
    
    QTableView::item:hover {{
        border-bottom: 1px solid #36436A;
    }}
    """

TABLE_HEADERS = """
    QHeaderView::section {{
        background-color: {};
        color: {};
        font-size: {}pt;
        font-family: "Calibri";
        padding: 2px;
        border-top: 1px solid #BAE2F0;
        border-right: 1px solid #B1B8BB;
        border-bottom: 2px solid #B1B8BB;
    }}
"""

# The vertical numbering on the left
VERTICAL_HEADERS = """
    QHeaderView::section {
        background-color: #E9E9E9;
        color: #6F6F6F;
        font: 8px "Nunito Sans";
        border: 1px solid #C7D1E0;
    }
"""

LEFT_LAYOUT = f"""
QWidget {{
        background-color: {title_bar_color};

}}
"""

hex_color = "#36436A"

LEFT_SIDE_BUTTONS_PRIMARY = f"""
    QPushButton {{
        background-color: {hex_color};
        color: white;
        font: 10pt "Nunito Sans";
        text-align: left; 
        padding: 5px 0px 5px 8px;
        border: none;
    }}

    QPushButton:hover {{
        background-color: #101020;
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

SECONDARY_BUTTONS = f"""
    QPushButton {{
        background-color: {hex_color};
        color: white;
        font: 10pt "Nunito Sans";
        text-align: left; 
        padding: 5px 0px 5px 8px;
        border: none;
    }}

    QPushButton:hover {{
        background-color: #101020;
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

CORNER_BUTTON = """
     QTableCornerButton::section {
        background-color: red;
    }
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: #4070A8;
        color: white;
        font: 14pt "Nunito Sans";
        padding: 10px 10px;
        border: none;
    }

    QPushButton:hover {
        background-color: #477EBC;
        color: white;
    }

    QPushButton:pressed {
        background-color: #5394DD;
        color: #FFFFFF;
        padding: 5px 5px;
    }
"""

TOAST_STYLES = """
    QLabel#toastTitle{
        font-size: 16px;
        color: white;
     }
    
    QLabel#toastMessage{
        font-size: 12px;
        color: white;
    }
    QPushButton#toastCloseButton{
        border: none;
        color: white;
        font-size: 12px;
    }
    QPushButton#toastCloseButton:hover{
    color:red;
    background-color: white;
    }
    
    QWidget#toastWidget {
    border: 30px;
    }
"""

REMINDER_VIEW = """
    QTimeEdit {
    background-color: #E4FAFF;
    color: #002E0E;
    font: 11pt "Nunito Sans";
    border: 1px solid #737477;
    padding: 0 0 0 0;
    margin: 0 7px 0 0;
    }  
"""

STATUS_BAR_STYLE = """
    QStatusBar {
    background-color: #131313;
    color: white;
    font: 8pt, "calibri";
    }
    
    QLabel {
    color: white;
    font: 8pt, "calibri";
    }
"""

RIBBON_SPACE = """

    QTabWidget::pane { /* The tab widget's content area */
    border-top: 0px solid;
    margin-bottom: 5px;
    }

    QTabWidget::tab-bar { /* tab-bar only, containing tabs like Home and View */
        left: 1px; /* Move the tabs slightly to right */
        background-color: red;
    }
    
    #TabContentWidget {  /* Custom object name for ribbon's content area QWidget */
        background: #DCDCDC;
        color: black;
        border: 1px solid #353535;
        border-radius: 12px;
    }
    
    QTabBar::tab {  /* individual tabs */
        background-color: #292929;
        color: white;
        font-size: 13px;
        padding: 7px;
    }

    QTabBar::tab:hover {
        background: #212121;
        color: white;
        border-bottom: 3px solid #DDEAF1;
        padding: 7px
    }
            
    QTabBar::tab:selected {
        background: #4E4E4E;
        color: white;
        border-bottom: 5px solid #DDEAF1;
        padding: 7px
    }
    
    QCheckBox#RibbonCheckbox {

    }
    
    QLabel#RibbonLabels{

    }
    
    QPushButton#RibbonButtons {
        background-color: white;
        color: black;
        border: none;
        border-radius: 3px;
        font-size: 12px;
        padding: 5px 8px;
    }
    
    QPushButton:hover#RibbonButtons {
        background-color: #3C3C3C;
        color: white;
    }
    
    QPushButton#ShowHideButton {
        background-color: #EAEAEA;
        
    }
"""

NOTIFICATION_WIN_STYLE = """
    QWidget {
        background-color: #FDFDFD;
    }
    QLabel {
        color: #333;
        font-size: 18px;
        padding: 8px;
    }
    QCheckBox {
        background-color: #F5F5F5;
        color: #333;
        spacing: 3;
        padding: 8px;
    }
    QPushButton {
        background-color: #1E88E5;
        color: white;
        border: none;
        padding: 8px 16px;
        font-size: 16px;
    }
    QPushButton:hover {
        background-color: #1A83DB;
    }
    
    QLineEdit {
        border: 1px solid #ccc;
        padding: 8px;
        font-size: 16px;
    }
"""

# When one value is specified, it applies the same padding or margin to all four sides (top, right, bottom,
# and left).
# When two values are specified, the first value applies to the top and bottom, and the second value
# applies to the left and right.
# When three values are specified, the first value applies to the top, the second to
# the left and right, and the third to the bottom.
# When four values are specified, they apply to the top, right,
# bottom, and left, in that order (clockwise).
