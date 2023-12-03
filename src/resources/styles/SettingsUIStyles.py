
RESET_BUTTON = ("""
    QPushButton#settingsResetButton {
        background-color: #3C3C3C;
        border: 1px solid #bdbdbd;
        border-radius: 5px;
        color: #ACACAC;
        font: 18px;
        }
    
    QPushButton:hover#settingsResetButton {
        border: 1px solid #6A6A6A;
        background-color: #696969;
        color: #D0D0D0;
        }
        
    QPushButton:pressed#settingsResetButton {
        background-color: #BFBFBF; 
        color: black;
        }
    """)

CHOOSE_COLOR_BUTTON = ("""
    QPushButton#chooseColorButton {{
        background-color: {bg_color};
        border: 2px solid #F7F7F7;
        padding: 4px 1px;
        font-size: 12px;
        }}
    """)

SETTINGS_DIALOG = (""" 
    QWidget#settingsUIClass {
        background-color: #f9f9f9;     
        }
    
    QLabel#settingsLabel {
        color: #333;
        font-size: 12px;
        }

    QPushButton#settingsWinButtons {
        background-color: #FFFFFF;
        border: 1px solid #0058C8;
        border-radius: 5px;
        padding: 1px 1px;
        font-size: 12px;
        color: black;
        }
        
    QPushButton#settingsWinButtons:hover {
        background-color: #e0eef9;
        }

    QPushButton#settingsWinButtons:disabled {
        background-color: #f9f9f9;
        color: #838383;
        border: 1px solid #B7B7B7;
        }
        
    QComboBox#settingsComboBox {
        border: 1px solid #ccc;
        font-size: 12px;
        }
    """)

LINE_SEPARATOR = ("""
    background-color: #C3C3C3;
    height: 1px;
    margin-top: 10px;
    margin-bottom: 1px;
    """)

# OK_CANCEL_APPLY_BUTTONS = ("""
#     QPushButton {
#         background-color: #ffffff;
#         border: 1px solid #bdbdbd;  /* Dark gray */
#         border-radius: 5px;
#         }
#
#     QPushButton:hover {
#         border: 1px solid #196ebf;
#         background-color: #e0eef9;
#         color: black;
#         }
#
#     QPushButton:pressed {
#         background-color: #D0D0D0;  /* Even darker gray */
#         }
#     """)