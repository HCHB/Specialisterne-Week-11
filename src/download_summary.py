import time
from datetime import datetime


class DownloadSummary:
    def __init__(self, folder_path, filename, title, parameters, downloads_verbose=False, failures_verbose=False):
        self._datetime = datetime.now()
        formatted_time = self._datetime.strftime('%Y-%m-%d-%H-%M')

        self._path = f'{folder_path}/{formatted_time} {filename}'
        self._title = title
        self._parameters = parameters

        self._start = time.time()
        self._end = None
        self._downloads = []
        self._failed = []
        self._verbose_downloads = downloads_verbose
        self._verbose_failures = failures_verbose

    def add_download(self, report_id, success):
        if success:
            self._downloads.append(report_id)
        else:
            self._failed.append(report_id)

    def save(self):
        self._end = time.time()

        summary = self._summary()

        with open(self._path, 'w') as writer:
            writer.write(summary)

            if self._verbose_downloads:
                writer.write(f'\nList of successful downloads:')
                for download in self._downloads:
                    writer.write(f'\n\t{download}')
                writer.write('\n')

            if self._verbose_failures:
                writer.write(f'\nList of failed downloads:')
                for failed in self._failed:
                    writer.write(f'\n\t{failed}')
                writer.write('\n')

    def _summary(self):
        return (f'Title: {self._title}\n'
                f'Parameters: \n{self._parameters_string(self._parameters, 1)}\n'
                f'\n'
                f'Start time: {self._datetime}\n'
                f'Runtime: {self._end - self._start}\n'
                f'Successful: {len(self._downloads)}\n'
                f'Failures: {len(self._failed)}\n')

    def _parameters_string(self, parameters, indentation):
        string_parameters = ''
        indent = '\t' * indentation

        for key, value in parameters.items():
            if isinstance(value, dict):
                value = f'\n{self._parameters_string(value, indentation+1)}'

            string_parameters += f'{indent}{key}: {value}\n'

        return string_parameters.rstrip()
