Commandline args

    Exercise> python -m src.controller --help
    usage: controller.py [-h] [-ew] [-ep [THREADPOOL_SIZE]] [-es [META_SAVE_RATE]] [-lf [LINK_SOURCE]] [-ls [LINK_SHEET]]
                         [-li [LINK_ID_COLUMN]] [-lc [LINK_COLUMNS ...]] [-mf [META_SOURCE]] [-ms [META_SHEET]]
                         [-mc [META_SUCCESS_COLUMN]] [-mo] [-df [DOWNLOAD_FOLDER]] [-dty [DOWNLOAD_TYPE]] [-dti [REQUEST_TIMEOUT]]
                         [-dc [REQUEST_CHUNKSIZE]] [-sd] [-sf]
    
    A script for taking links from a excel file and downloading pdf reports from the internet
    
    optional arguments:
      -h, --help            show this help message and exit
      -ew, --report_overwrite
                            Overwrite existing reports
      -ep [THREADPOOL_SIZE], --threadpool_size [THREADPOOL_SIZE]
                            The amount of threads dedicated to downloading reports
      -es [META_SAVE_RATE], --meta_save_rate [META_SAVE_RATE]
                            Number of attempted downloads before saving to the meta file
      -lf [LINK_SOURCE], --link_source [LINK_SOURCE]
                            File path for the link source
      -ls [LINK_SHEET], --link_sheet [LINK_SHEET]
                            Sheet name in the link source file
      -li [LINK_ID_COLUMN], --link_id_column [LINK_ID_COLUMN]
                            ID column name in the link source file
      -lc [LINK_COLUMNS ...], --link_columns [LINK_COLUMNS ...]
                            A list of column names where the download links are in the link source file
      -mf [META_SOURCE], --meta_source [META_SOURCE]
                            File path for the meta file
      -ms [META_SHEET], --meta_sheet [META_SHEET]
                            Sheet name in the meta file
      -mc [META_SUCCESS_COLUMN], --meta_success_column [META_SUCCESS_COLUMN]
                            The column name in the meta file where download success is written
      -mo, --sort_metadata  Sort the metadata at the end of the execution
      -df [DOWNLOAD_FOLDER], --download_folder [DOWNLOAD_FOLDER]
                            Folder path for where to save reports
      -dty [DOWNLOAD_TYPE], --download_type [DOWNLOAD_TYPE]
                            The expected report file type
      -dti [REQUEST_TIMEOUT], --request_timeout [REQUEST_TIMEOUT]
                            Seconds before timing out a http request
      -dc [REQUEST_CHUNKSIZE], --request_chunksize [REQUEST_CHUNKSIZE]
                            The chunk size that are gathered from the http request before writing it to the file
      -sd, --verbose_downloads
                            Boolean for if the download summary should write all the downloaded IDs
      -sf, --verbose_failures
                            Boolean for if the download summary should write all the failed IDs
