import os
import PyPDF2
import requests


class PDFDownloader:
    def __init__(self, chunk_size=8192, timeout=10):
        self._chunk_size = chunk_size
        self._timeout = timeout

    def download(self, url, filepath):
        file_exists = os.path.isfile(filepath)
        download_path = self._get_download_path(filepath, file_exists)

        try:
            self._download(url, download_path)
            download_verified = self._verify_file(download_path)
            self._cleanup(filepath, file_exists, download_path, download_verified)
            return download_verified
        except Exception as e:
            if os.path.isfile(download_path):
                os.remove(download_path)
            return False

    def _cleanup(self, filepath, file_exists, download_path, download_verified):
        if not download_verified:
            os.remove(download_path)
            return False

        if file_exists:
            os.remove(filepath)
            os.rename(download_path, filepath)
            return True

    def _get_download_path(self, filepath, file_exists):
        if file_exists:
            download_path = f'{filepath}.tmp'
        else:
            download_path = filepath

        return download_path

    def _verify_file(self, path):
        if os.path.isfile(path):
            try:
                reader = PyPDF2.PdfReader(path)
                if len(reader.pages) > 0:
                    return True

            except Exception as e:
                pass

        return False

    def _download(self, url, filepath):
        with requests.get(url, stream=True, timeout=self._timeout) as response:
            response.raise_for_status()

            with open(filepath, 'wb') as writer:
                for chunk in response.iter_content(chunk_size=self._chunk_size):
                    writer.write(chunk)

        return True
