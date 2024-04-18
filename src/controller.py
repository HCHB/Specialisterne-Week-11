import glob
import os
from concurrent.futures import ThreadPoolExecutor
import concurrent

from src.download_summary import DownloadSummary
from src.link_reader import LinkReader
from src.meta_writer import MetaWriter
from src.pdf_downloader import PDFDownloader


class Controller:
    def __init__(self):
        self._config = {}

        self._pool_size = 50     # TODO Adjust value
        self._overwrite_reports = True  # TODO toggle

        self._config['Execution'] = {
            'threadpool size': self._pool_size,
            'overwrite reports': self._overwrite_reports
        }

        self._init_source()
        self._init_meta()
        self._init_downloader()
        self._init_summarizer()


    def _init_source(self):
        self._link_reader = LinkReader()
        self._link_source = r'C:\Users\KOM\PycharmProjects\Week 11 - Exercise\data\GRI_2017_2020_test.xlsx'
        # self._link_source = r'C:\Users\KOM\Documents\My documents\Week 11 - Exercise\Data\GRI_2017_2020 (1).xlsx'
        self._link_sheet_name = '0'
        self._IDColumn = 'BRnum'
        self._link_columns = ['Pdf_URL', 'Report Html Address']

        self._config['Link source'] = {
            'file': self._link_source,
            'sheet': self._link_sheet_name,
            'ID column': self._IDColumn,
            'link columns': self._link_columns
        }

    def _init_meta(self):
        self._meta_writer = MetaWriter()
        self._meta_path = r'C:\Users\KOM\PycharmProjects\Week 11 - Exercise\data\Metadata2024.xlsx'
        self._meta_sheet_name = '0'
        self._download_success_column = 'pdf_downloaded'
        self._meta_writer.open_sheet(self._meta_path, self._meta_sheet_name, index=self._IDColumn)

        self._config['Meta file'] = {
            'file': self._meta_path,
            'sheet': self._meta_sheet_name,
            'success column': self._download_success_column
        }

    def _init_downloader(self):
        self._downloader = PDFDownloader()
        self._report_path = r'C:\Users\KOM\PycharmProjects\Week 11 - Exercise\data\Reports'
        self._report_type = 'pdf'

        self._config['Downloader'] = {
            'download path': self._report_path,
            'report type': self._report_type,
        }

    def _init_summarizer(self):
        self._verbose_downloads = False
        self._verbose_failures = False

        self._config['Summary'] = {
            'verbose downloads': self._verbose_downloads,
            'verbose failures': self._verbose_failures
        }

        self._summarizer = DownloadSummary(folder_path=f'{self._report_path}',
                                           filename='summary.txt',
                                           title=f'{self._report_type} download',
                                           parameters=self._config,
                                           downloads_verbose=self._verbose_downloads,
                                           failures_verbose=self._verbose_failures)

    def run(self):
        # check for files already downloaded
        existing_files = self._get_existing_files(self._report_path, self._report_type)

        # Read file
        self._link_reader.load(self._link_source, self._link_sheet_name, self._IDColumn, self._link_columns)

        # Filter dataframe
        self._link_reader.filter(self._link_columns, existing_files, self._overwrite_reports)

        # Read rows
        rows = self._link_reader.get_values()

        # Download reports
        self._download_reports(rows)

        # Ensure that metafile dataframe is saved
        self._meta_writer.write()

        # Write summary
        self._summarizer.save()

    def _download_reports(self, rows, meta_buffer=100):
        count = 0
        with ThreadPoolExecutor(max_workers=self._pool_size) as pool:
            futures = [pool.submit(self._download_row, index, row) for index, row in rows]

            for future in concurrent.futures.as_completed(futures):
                count += 1
                success, index, download_result = future.result()
                print(f'{index}: {download_result}')  # TODO remove print

                self._meta_writer.add_value(index, column_name=self._download_success_column, value=download_result)
                self._summarizer.add_download(index, success)

                if count > meta_buffer:
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
            return success, index, success_message
        else:
            return success, index, error_message

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
