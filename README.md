# Stream unzipping a large file to S3 with Python

This repository serves as a proof of concept for unzipping a large file in a resource-constrained compute environment. 

The data set I tested with was from https://smoosavi.org/datasets/us_accidents. It's 2.25 million lines, but I cut it down to 1 million lines for the sake of testing. At 1 million lines, the gzipped file was roughly `69MB` and the unzipped file was roughly `385MB`. The unzipped size dictates the values for memory and disk space used below in testing the resource-constrained image.

## Project Structure

-  src/ - folder is shared between the container and host
    - requirements.txt - our Python script's dependencies
    - main.py - the Python script for downloading and decompressing the file in S3
- Dockerfile - used to build our image that can run the Python script 

## Setup

1. An AWS account is required for testing Scenario Three
1. Find a large dataset and gzip it
1. Upload the data file to S3
1. Modify the `bucket_name` and `object_name` in `main.py` to reference your bucket and file
1. Build our docker image: `docker build -t python-streams .`

Run the docker container with the following command:

```
docker run -it \
  --memory=300m \
  --memory-swap=300m \
  --mount type=tmpfs,destination=/usr/src/data,tmpfs-size=300000000 \
  --volume=$PWD/src:/usr/src/mount \
  --env AWS_ACCESS_KEY_ID \
  --env AWS_SECRET_ACCESS_KEY \
  --env AWS_DEFAULT_REGION \
  python-streams:latest /bin/bash
```

This limits our container to 300MB of memory and memory swap and roughly 300MB of disk space in a temporary file storage space. Because my sample file was over 300MB uncompressed, this allowed me to test exhausting memory and disk space. If you test with a difference file size, you'll want to modify the memory, memory-swap, and tmpfs-size parameters. 

*Note: Scenarios One and Two fail on purpose*

## Scenarios

## Unzip to memory

1. Edit the `src/main.py` file and uncomment `load_file_into_memory()` at the bottom
1. Inside the running container `cd ../mount`
1. Run `python main.py`

Example run:
```
root@a1f9f68a98cc:/usr/src/mount# python main.py 
Downloading file from us-accident-data/US_Accidents_May19_1M.csv.gz to /usr/src/data/US_Accidents_May19_1M.csv.gz
Killed
```

The process was killed due to exhausting memory while decompressing.

## Unzip to disk

1. Edit the `src/main.py` file and uncomment `load_file_into_disk()` at the bottom
1. Inside the running container `cd ../mount`
1. Run `python main.py`

Example run:
```
 root@8ffd66c79af0:/usr/src/mount# python main.py 
 Downloading file from us-accident-data/US_Accidents_May19_1M.csv.gz to /usr/src/data/US_Accidents_May19_1M.csv.gz
 Traceback (most recent call last):
   File "main.py", line 75, in <module>
     load_file_into_disk()
   File "main.py", line 56, in load_file_into_disk
     shutil.copyfileobj(file_in, file_out)
   File "/usr/local/lib/python3.8/shutil.py", line 205, in copyfileobj
     fdst_write(buf)
 OSError: [Errno 28] No space left on device
```

The process was killed due to exhausting disk space while decompressing.

## Unzip to S3 via stream

1. Edit the `src/main.py` file and uncomment `stream_unzip_to_s3()` at the bottom
1. Inside the running container `cd ../mount`
1. Run `python main.py`

Example run:
```
root@3bb3c79ce322:/usr/src/mount# python main.py 
Downloading file from us-accident-data/US_Accidents_May19_1M.csv.gz to /usr/src/ data/US_Accidents_May19_1M.csv.gz
Decompressing file /usr/src/data/US_Accidents_May19_1M.csv.gz and uploading to /usr/src/data/US_Accidents_May19_1M.csv
Finished decompressing and sending to S3
```

It worked! The file was downloaded and successfully uploaded back to S3 while decompressing it. The magic is in these two lines:

```
    with gzip.open(downloaded_file_path, "rb") as data:
        s3.upload_fileobj(data, bucket_name, decompressed_filename)
```

We successfully decompressed a file that was larger than both the memory and disk space available in our runtime environment. 

### Notes

To view the free memory inside the running container, use
`cat /proc/meminfo` and you'll see values for MemTotal, MemFree, and MemAvailable. 

To view the free disk space inside the running container, use `df -h`. 
You'll probably see several disks, but the one to note is listed as:

`tmpfs           ###M     0  ###M   0% /usr/src/data` 
