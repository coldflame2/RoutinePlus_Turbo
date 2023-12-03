TABLE_STYLES = ("""
    QTableView {
        background-color: #646879;
        font-size: 10pt;
    }

    QTableView::item {
        border-top: 2px solid #33384F;
        border-bottom: 5px solid #33384F;
        border-right: 3px solid #33384F;
        background-color: #F0F0F0;
        font-size: 10pt;

    }

    QTableView::item:hover {
        border-top: 1px solid #000DF0;
        border-bottom: 2px solid #33384F;
        border-right: 3px solid #33384F;
        background-color: #E6F0F0;

        font-size: 12pt;
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
