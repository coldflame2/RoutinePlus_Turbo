from src.resources.styles import all_styles


class TableStyles:
    def __init__(self):
        self.apply_settings()
        self.apply_headers_styles()
        self.apply_table_styles()

    def apply_settings(self):
        self.apply_headers_styles()
        self.apply_table_styles()

    def apply_headers_styles(self):
        return all_styles.HEADERS_STYLE

    def apply_table_styles(self):
        return all_styles.TABLE_STYLES