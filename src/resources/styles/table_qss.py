TABLE_STYLES = ("""
    QTableView {
        background-color: #646879;
        font-size: 10pt;
        gridline-color: transparent;
    }

    QTableView::item {
        background-color: #F0F0F0;
        font-size: 10pt;
        
        border-top: 2px solid #646879;
        border-right: 1px solid #646879;
        border-bottom: 4px solid #646879;
        border-left: 0px solid #646879;
        
        padding: 5px 5px 5px 8px; /*top, right, bottom, left*/

    }

    QTableView::item:hover {
        background-color: #E6F0F0;
        font-size: 12pt;

        border-top: 1px solid #646879;
        border-right: 1px solid #646879;
        border-bottom: 4px solid #36436A;
        border-left: 0px solid #646879;   
         
        padding: 0px 5px 0px 8px; /*top, right, bottom, left*/
    
    }
    
    QTableView::item:selected {
        background-color: #B0BDE3;
        color: black;
    }
    
    QTableView::item:focus {
        outline: none;
    }

    
    QHeaderView::section {
        background-color: #36436A;
        color: #DDEAF3;
        font-size: 14pt;
        font-family: "Calibri";
        border-top: 1px solid #33384F;
        border-right: 3px solid #33384F;
        border-bottom: 1px solid #33384F;
        border-left: 1px solid #33384F;            
    }


    QTableCornerButton::section {
        background-color: #36436A;
    }

""")
