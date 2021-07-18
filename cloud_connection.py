import os

from google.cloud import storage

import util


def get_existing_tables_from_cloud():
    print("Downloading existing tables")
    storage_client = storage.Client()
    bucket_name = os.getenv("CLOUD_BUCKET")
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=f'{util.crawl_path}/')
    for blob in blobs:
        blob.download_to_filename(blob.name.replace(f'{util.crawl_path}/', f'{util.path}/'))
    blob = bucket.blob('categories')
    blob.download_to_filename(f'{util.config_path}/config_categories')
    blob = bucket.blob('last_crawl')
    blob.download_to_filename(f'{util.config_path}/last_crawl.txt')
    print("Succesfully downloaded existing data")