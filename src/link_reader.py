import pandas


class LinkReader:
    def __init__(self):
        self._dataframe = None

    def load(self, path, sheet_name, index=None, column_names=None):
        if index and column_names:
            column_names = [index] + column_names

        dataframe = pandas.read_excel(path, sheet_name=sheet_name, index_col=index, usecols=column_names)
        self._dataframe = dataframe
        return dataframe

    def filter(self, columns, filenames, overwrite=False):
        self.filter_links(columns)
        if not overwrite:
            self.filter_paths(filenames)

    def filter_links(self, columns):
        non_empty_mask = ~self._dataframe[columns].isnull().all(axis=1)
        self._dataframe = self._dataframe[non_empty_mask]

    def filter_paths(self, filenames):
        mask = ~self._dataframe.index.isin(filenames)
        self._dataframe = self._dataframe[mask]

    def get_values(self):
        for row in self._dataframe.iterrows():
            yield row
