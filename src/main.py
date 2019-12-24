from pathlib import Path, PurePath
import subprocess
import gzip
import shutil

import boto3

s3 = boto3.client("s3")
# The S3 bucket and object used for testing.
# Replace these with your own bucket and object to test with
bucket_name = "us-accident-data"
object_name = "US_Accidents_May19_1M.csv.gz"


def stream_unzip_to_s3():
    downloaded_file_path = download_file(bucket_name, object_name)
    decompressed_filename = downloaded_file_path.strip(".gz")

    print(
        f"Decompressing file {downloaded_file_path} and uploading to {decompressed_filename}")

    with gzip.open(downloaded_file_path, "rb") as data:
        s3.upload_fileobj(data, bucket_name, decompressed_filename)

    print("Finished decompressing and sending to S3")


def download_file(bucket_name, object_name):
    # From object_name, get the name of the file itself
    file_name = PurePath(object_name).name

    file_path = f"/usr/src/data/{file_name}"

    print(f"Downloading file from {bucket_name}/{object_name} to {file_path}")

    s3.download_file(bucket_name, object_name, file_path)

    return file_path


def load_file_into_disk():
    downloaded_file_path = download_file(bucket_name, object_name)

    with gzip.open(downloaded_file_path, 'r') as file_in, open(downloaded_file_path.strip(".gz"), 'wb') as file_out:
        shutil.copyfileobj(file_in, file_out)

    print(f"Unzipped file to content length: {len(file_out)}")


def load_file_into_memory():
    downloaded_file_path = download_file(bucket_name, object_name)

    gzip_file = gzip.GzipFile(filename=downloaded_file_path, mode='rb')

    unzipped_file_path = downloaded_file_path.strip(".gz")

    with open(unzipped_file_path, 'w') as outfile:
        outfile.write(gzip_file.read())

    print(f"Unzipped file to content length: {len(file_out)}")


# Below are the 3 methods of unzipping, uncomment one and
# run this script with `python main.py` to test one out
# See the README for which Docker command to run to test each scenario

# Scenario One: Unzipping into memory
# load_file_into_memory()

# Scenario Two: Unzipping to disk
# load_file_into_disk()

# Scenario Three: Stream unzipping
# stream_unzip_to_s3()
