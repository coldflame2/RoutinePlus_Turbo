
class TableState:

    def __init__(self, view):
        self.view = view
        self.selected_row = None
        self.selected_column = None
        self.clicked_index = None
        self.hovered_row = None
        self.btn_hover_state = False  # True or False (New task button on Sidebar)

    def update_btn_hover_state(self, bool_value):
        self.btn_hover_state = bool_value

    def updated_selected_row_and_col(self, index):  # Called when cell clicked
        self.clicked_index = index
        self.selected_row = index.row()
        self.selected_column = index.column()

    def update_hovered_row(self, row):
        self.hovered_row = row
