import subprocess
import gzip

import boto3

s3 = boto3.client("s3")
bucket_name = "us-accident-data"
object_name = "US_Accidents_May19.tar.gz"

from pathlib import Path, PurePath

def _decompress_file(file_path, s3_path):
    decompressed_filename = s3_path.strip(".gz")
    
    _LOGGER.info("Decompressing file %s and uploading to %s", file_path, decompressed_filename)

    with gzip.open(file_path, "rb") as data:
        s3.upload_fileobj(data, EnvVar.data_pipeline_bucket, decompressed_filename)

    return decompressed_filename

def _download_file(bucket_name, object_name):
    # From object_name, get the name of the file itself
    file_name = PurePath(object_name).name

    file_path = f"/usr/src/data/{file_name}"

    print(f"Downloading file from {bucket_name}/{object_name} to {file_path}")

    s3.download_file(bucket_name, object_name, file_path)

    return file_path

def load_raw_data():
    bucket_name = "us-accident-data"
    object_name = "US_Accidents_May19.tar.gz"

    downloaded_file_path = _download_file(bucket_name, object_name)

    decompressed_file_name = _decompress_file(downloaded_file_path, data_filename)    

def load_file_into_memory():
    downloaded_file_path = _download_file(bucket_name, object_name)

    gzip_file = gzip.GzipFile(fileobj=downloaded_file_path, mode='rb')

    with open(downloaded_file_path.strip(".gz"), 'w') as outfile:
        outfile.write(gzip_file.read())

def load_file_onto_disk():
    downloaded_file_path = _download_file(bucket_name, object_name)

    gzip_file = gzip.GzipFile(fileobj=downloaded_file_path, mode='rb')

    with gzip.open(downloaded_file_path, 'rb') as f:
        file_content = f.read()

load_file_into_memory()

# Try to unzip and hold in memory
# Try to unzip to disk
# Stream