import hashlib
import os
from typing import List

import boto3
from py_common_utility.utils import file_utils


def get_etag(bucket_name, key):
    try:
        s3 = boto3.client('s3')
        # Fetch object metadata
        response = s3.head_object(Bucket=bucket_name, Key=key)
        # Extract and return the ETag
        return response.get('ETag', '').strip('"')
    except Exception as e:
        print(f"Error fetching ETag: {e}")
        return None


def list_etag_in_folder(bucket_name, folder_prefix) -> List[dict]:
    try:
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' in response:
            return [
                {"Key": obj['Key'], "ETag": obj['ETag'].strip('"')}
                for obj in response['Contents']
            ]
        else:
            print("No objects found in the folder.")
            return []
    except Exception as e:
        print(f"Error listing objects: {e}")
        return []


def hash_in_folder(bucket_name, folder_prefix) -> str:
    etag_list = list_etag_in_folder(bucket_name, folder_prefix)
    combined_etags = ",".join([item['Key'] + ":" + item['ETag'] for item in etag_list])
    final_hash = hashlib.md5(combined_etags.encode()).hexdigest()
    return final_hash

def download_folder_from_s3(bucket_name, s3_folder, local_dir):
    """
    Download an entire folder from an S3 bucket to a local directory.

    :param bucket_name: str. Name of the S3 bucket.
    :param s3_folder: str. Path of the folder in the S3 bucket.
    :param local_dir: str. Local directory to save the downloaded folder.
    """
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')

    for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_folder):
        if 'Contents' in page:
            for obj in page['Contents']:
                # Get the file path from the S3 object key
                s3_key = obj['Key']
                local_file_path = os.path.join(local_dir, s3_key)

                # Create local directories if they do not exist
                file_utils.ensure_directory_exists(str(local_file_path))

                try:
                    s3.download_file(bucket_name, s3_key, local_file_path)
                    print(f"Downloaded {s3_key} to {local_file_path}")
                except Exception as e:  # work on python 3.x
                    print('Failed to upload to ftp: ' + str(e))
                # Download the file


if __name__ == '__main__':
    # Example usage
    _bucket_name = 'dsa-evr'
    s3_folder = 'company/'  # Adjusted to your specific S3 path  # Folder path in S3
    local_dir = '/tmp/dsa/evr/'  # Local directory where you want to save the folder
    # download_folder_from_s3(_bucket_name, s3_folder, local_dir)
    print("HI~ DONE")
    hash_list = list_etag_in_folder(_bucket_name, s3_folder)
    print(hash_list)
    a_etag = get_etag(_bucket_name, "company/0ed8be99-ed68-40ed-a1df-25f077d11459/header.bin")
    print(a_etag)
    dir_hash = hash_in_folder(_bucket_name, s3_folder)
    print(dir_hash)
