import requests


class PDFDownloader:
    def __init__(self, chunk_size=8192, timeout=10):
        self._chunk_size = chunk_size
        self._timeout = timeout

    def download(self, url, filepath):
        # TODO check file exists, temp
        with requests.get(url, stream=True, timeout=self._timeout) as response:
            response.raise_for_status()

            with open(filepath, 'wb') as writer:
                for chunk in response.iter_content(chunk_size=self._chunk_size):
                    writer.write(chunk)

        return True
