import glob
import os
from concurrent.futures import ThreadPoolExecutor
import concurrent
import argparse


from src.download_summary import DownloadSummary
from src.link_reader import LinkReader
from src.meta_writer import MetaWriter
from src.pdf_downloader import PDFDownloader


class Controller:
    def __init__(self):
        args = self._read_arguments()

        self._config = {}

        self._pool_size = args.threadpool_size
        self._overwrite_reports = args.report_overwrite
        self._meta_save_rate = args.meta_save_rate

        self._config['Execution'] = {
            'threadpool size': self._pool_size,
            'overwrite reports': self._overwrite_reports,
            'meta save rate': self._meta_save_rate
        }

        self._init_source(args)
        self._init_meta(args)
        self._init_downloader(args)
        self._init_summarizer(args)

        from pprint import pprint
        pprint(self._config)

    def _read_arguments(self):
        parser = argparse.ArgumentParser(description='A script for taking links from a excel file and downloading pdf '
                                                     'reports from the internet')

        # Execution arguments
        parser.add_argument('-ew', '--report_overwrite', action='store_true',
                            default=False,
                            help='Overwrite existing reports')
        parser.add_argument('-ep', '--threadpool_size', nargs='?', type=int,
                            default=100,
                            help='The amount of threads dedicated to downloading reports')
        parser.add_argument('-es', '--meta_save_rate', nargs='?', type=int,
                            default=100,
                            help='Number of attempted downloads before saving to the meta file')

        # Source arguments
        parser.add_argument('-lf', '--link_source', nargs='?', type=str,
                            default=r'./data/GRI_2017_2020 (1).xlsx',
                            help='File path for the link source')
        parser.add_argument('-ls', '--link_sheet', nargs='?', type=str,
                            default='0',
                            help='Sheet name in the link source file')
        parser.add_argument('-li', '--link_id_column', nargs='?', type=str,
                            default='BRnum',
                            help='ID column name in the link source file')
        parser.add_argument('-lc', '--link_columns', nargs='*', type=str,
                            default=['Pdf_URL', 'Report Html Address'],
                            help='A list of column names where the download links are in the link source file')

        # Meta file arguments
        parser.add_argument('-mf', '--meta_source', nargs='?', type=str,
                            default=r'./data/Metadata2024.xlsx',
                            help='File path for the meta file')
        parser.add_argument('-ms', '--meta_sheet', nargs='?', type=str,
                            default='0',
                            help='Sheet name in the meta file')
        parser.add_argument('-mc', '--meta_success_column', nargs='?', type=str,
                            default='pdf_downloaded',
                            help='The column name in the meta file where download success is written')
        parser.add_argument('-mo', '--sort_metadata', action='store_true',
                            default=True,
                            help='Sort the metadata at the end of the execution')

        # Download arguments
        parser.add_argument('-df', '--download_folder', nargs='?', type=str,
                            default=r'./data/Reports',
                            help='Folder path for where to save reports')
        parser.add_argument('-dty', '--download_type', nargs='?', type=str,
                            default='pdf',
                            help='The expected report file type')
        parser.add_argument('-dti', '--request_timeout', nargs='?', type=int,
                            default=10,
                            help='Seconds before timing out a http request')
        parser.add_argument('-dc', '--request_chunksize', nargs='?', type=int,
                            default=8192,
                            help='The chunk size that are gathered from the http request before writing it to the file')

        # Summarizer arguments
        parser.add_argument('-sd', '--verbose_downloads', action='store_true',
                            default=False,
                            help='Boolean for if the download summary should write all the downloaded IDs')
        parser.add_argument('-sf', '--verbose_failures', action='store_true',
                            default=False,
                            help='Boolean for if the download summary should write all the failed IDs')

        try:
            args = parser.parse_args()
        except SystemExit as e:
            if e.code != 0:
                parser.print_help()
            exit(e.code)

        return args

    def _init_source(self, args):
        self._link_reader = LinkReader()
        self._link_source = args.link_source
        self._link_sheet_name = args.link_sheet
        self._IDColumn = args.link_id_column
        self._link_columns = args.link_columns

        self._config['Link source'] = {
            'file': self._link_source,
            'sheet': self._link_sheet_name,
            'ID column': self._IDColumn,
            'link columns': self._link_columns
        }

    def _init_meta(self, args):
        self._meta_writer = MetaWriter()
        self._meta_path = args.meta_source
        self._meta_sheet_name = args.meta_sheet
        self._download_success_column = args.meta_success_column
        self._sort_metadata = args.sort_metadata
        self._meta_writer.open_sheet(self._meta_path, self._meta_sheet_name, index=self._IDColumn)

        self._config['Meta file'] = {
            'file': self._meta_path,
            'sheet': self._meta_sheet_name,
            'success column': self._download_success_column,
            'sort': self._sort_metadata
        }

    def _init_downloader(self, args):
        self._download_timeout = args.request_timeout
        self._download_chunk_size = args.request_chunksize

        self._downloader = PDFDownloader(timeout=self._download_timeout, chunk_size=self._download_chunk_size)
        self._report_path = args.download_folder
        self._report_type = args.download_type

        self._config['Downloader'] = {
            'download path': self._report_path,
            'report type': self._report_type,
            'download timeout': self._download_timeout,
            'download chunk size': self._download_chunk_size
        }

    def _init_summarizer(self, args):
        self._verbose_downloads = args.verbose_downloads
        self._verbose_failures = args.verbose_failures

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
        self._download_reports(rows, self._meta_save_rate)

        # Ensure that metafile dataframe is saved
        self._meta_writer.write(sort=self._sort_metadata)

        # Write summary
        self._summarizer.save()

    def _download_reports(self, rows, meta_buffer=100):
        count = 0
        with ThreadPoolExecutor(max_workers=self._pool_size) as pool:
            futures = [pool.submit(self._download_row, index, row) for index, row in rows]

            for future in concurrent.futures.as_completed(futures):
                count += 1
                success, index, download_result = future.result()
                # print(f'{index}: {download_result}')  # TODO remove print

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
