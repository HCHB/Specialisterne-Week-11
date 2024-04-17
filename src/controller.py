import glob
import os

from src.link_reader import LinkReader
from src.meta_writer import MetaWriter
from src.pdf_downloader import PDFDownloader


class Controller:
    def __init__(self):
        self._link_reader = LinkReader()
        self._link_source = r'C:\Users\KOM\PycharmProjects\Week 11 - Exercise\data\GRI_2017_2020.xlsx'
        self._link_source = r'C:\Users\KOM\Documents\My documents\Week 11 - Exercise\Data\GRI_2017_2020 (1).xlsx'
        self._sheet_name = '0'
        self._IDColumn = 'BRnum'
        self._link_columns = ['Pdf_URL', 'Report Html Address']

        self._meta_writer = MetaWriter()
        self._meta_path = r'C:\Users\KOM\PycharmProjects\Week 11 - Exercise\data\Metadata2024.xlsx'
        self._meta_writer.open_sheet(self._meta_path, '0', index=self._IDColumn)
        self._download_success_column = 'pdf_downloaded'

        self._downloader = PDFDownloader()
        self._report_path = r'C:\Users\KOM\PycharmProjects\Week 11 - Exercise\data\tmp_reports'
        self._report_type = 'pdf'

    def run(self):
        # check for files already downloaded
        existing_files = self._get_existing_files(self._report_path, self._report_type)

        # read file
        self._link_reader.load(self._link_source, self._sheet_name, self._IDColumn, self._link_columns)
        # Filter dataframe  TODO rethink placement
        self._link_reader.filter_links(self._link_columns)
        self._link_reader.filter_paths(existing_files)  # TODO conditional on if forced update

        rows = self._link_reader.get_values()

        self._download_reports(rows)

        self._meta_writer.write()

    def _download_reports(self, rows, write_when=100):
        count = 0
        for index, row in rows:
            count += 1
            download_result = self._download_row(index, row)
            self._meta_writer.add_value(index, column_name=self._download_success_column, value=download_result)

            if count > write_when:
                self._meta_writer.write()
                count = 0

    def _download_row(self, index, row):
        success = False
        success_message = 'success'
        error_message = 'download failed'

        for link_column in self._link_columns:
            try:
                success = self._download_link(index, row, link_column)

                if success:
                    break
            except Exception as e:
                # error_message = f'{error_message}\n{e}'
                print(f'{index}: {e}')

        if success:
            return success_message
        else:
            return error_message

    def _download_link(self, index, row, link_column):
        url = row[link_column]

        if not isinstance(url, str):
            return False

        filepath = f'{self._report_path}/{index}.{self._report_type}'

        success = self._downloader.download(url=url, filepath=filepath)

        return success

    def _get_existing_files(self, path, filetype):
        paths = glob.glob(os.path.join(path, f"*.{filetype}"))
        filenames = [os.path.basename(path)[:-4] for path in paths]
        return filenames


if __name__ == '__main__':
    controller = Controller()
    controller.run()

    print('Program ended')
