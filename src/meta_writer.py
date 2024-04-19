import pandas


class MetaWriter:
    def __init__(self):
        self._dataframe = None
        self._path = None
        self._sheet = None

    def open_sheet(self, path, sheet_name, index=None):
        self._dataframe = pandas.read_excel(path, sheet_name=sheet_name, index_col=index)
        self._path = path
        self._sheet = sheet_name

    def add_value(self, index, column_name, value):
        if index in self._dataframe.index:
            self._dataframe.loc[index, column_name] = value
        else:
            self._dataframe.loc[index] = pandas.Series({column_name: value})

    def write(self, sort=False):
        if sort:
            self._dataframe.sort_index(inplace=True)

        with pandas.ExcelWriter(self._path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            self._dataframe.to_excel(writer, sheet_name=self._sheet, index=True)
