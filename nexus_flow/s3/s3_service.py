import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Iterator

import boto3


@dataclass
class UploadFileObj:
    dest_path: str
    local_path: str


class S3Service:
    def __init__(self, region_name=None, aws_access_key_id=None, aws_secret_access_key=None):
        self.s3 = boto3.client(
            's3',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def list_folders(self, bucket_name: str, prefix: str) -> List[str]:
        paginator = self.s3.get_paginator('list_objects_v2')
        folders = []
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter='/'):
            if 'CommonPrefixes' in page:
                for cp in page['CommonPrefixes']:
                    folders.append(cp['Prefix'])
        return folders

    def delete_file(self, bucket_name: str, s3_key: str):
        """
        Delete a file from an S3 bucket using its key.
        """
        response = self.s3.delete_object(Bucket=bucket_name, Key=s3_key)
        print(f"Deleted {s3_key} from bucket {bucket_name}.")
        return response

    def get_file_content(self, bucket_name: str, s3_key: str, default_value: str = '') -> str:
        """
        Get the content of a file from an S3 bucket using its key.
        """
        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=s3_key)
            content = response['Body'].read().decode('utf-8')  # Assuming text-based file
            print(f"Successfully retrieved content from {s3_key}")
            return content
        except Exception as e:
            print(f"Failed to get content from {s3_key}: {e}")
            return default_value

    def get_etag(self, bucket_name: str, key: str):
        """
        Get the ETag for a specific file in an S3 bucket.
        """
        try:
            response = self.s3.head_object(Bucket=bucket_name, Key=key)
            return response.get('ETag', '').strip('"')
        except Exception as e:
            print(f"Error fetching ETag: {e}")
            return None

    def list_etag_in_folder(self, bucket_name: str, folder_prefix: str, file_extensions=None) -> List[dict]:
        """
        List all objects in a folder and return their keys and ETags.
        """
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' in response:
            return [
                {"Key": obj['Key'], "ETag": obj['ETag'].strip('"')}
                for obj in response['Contents']
                if file_extensions is None or any(obj['Key'].endswith(ext) for ext in file_extensions)
            ]
        else:
            print("No objects found in the folder.")
            return []

    def hash_in_folder(self, bucket_name: str, folder_prefix: str) -> str:
        """
        Combine all ETags in a folder to produce a single MD5 hash.
        """
        etag_list = self.list_etag_in_folder(bucket_name, folder_prefix)
        combined_etags = ",".join([item['Key'] + ":" + item['ETag'] for item in etag_list])
        final_hash = hashlib.md5(combined_etags.encode()).hexdigest()
        return final_hash

    def download_folder(self, bucket_name: str, s3_folder: str, local_dir: str, file_extensions=None):
        """
        Download an entire folder from S3 to a local directory.
        """
        paginator = self.s3.get_paginator('list_objects_v2')

        for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_folder):
            if 'Contents' in page:
                for obj in page['Contents']:
                    s3_key = obj['Key']

                    # Filter by file extension
                    if file_extensions and not any(s3_key.endswith(ext) for ext in file_extensions):
                        continue

                    local_file_path = os.path.join(local_dir, os.path.relpath(s3_key, s3_folder))
                    Path(local_file_path).parent.mkdir(parents=True, exist_ok=True)

                    try:
                        self.s3.download_file(bucket_name, s3_key, local_file_path)
                        print(f"Downloaded {s3_key} to {local_file_path}")
                    except Exception as e:
                        print(f"Failed to download {s3_key}: {e}")

    def upload_all(self, bucket_name: str, doc_iterator: Iterator[UploadFileObj]) -> str:
        """
        Upload multiple files to an S3 bucket.
        """
        for item in doc_iterator:
            file_path_obj = Path(item.local_path)
            if not file_path_obj.exists():
                continue
            s3_key = item.dest_path
            if file_path_obj.is_file():
                self.upload_a_file(bucket_name, s3_key, file_path_obj)
            if file_path_obj.is_dir():
                self.upload_a_dir(bucket_name=bucket_name,local_folder=str(file_path_obj),dest_folder=s3_key)

        return "Upload completed."

    def upload_a_file(self, bucket_name: str, s3_key: str, file_path_obj: Path) -> str:
        try:
            self.s3.upload_file(str(file_path_obj), bucket_name, s3_key)
            print(f"Uploaded: {file_path_obj} to s3://{bucket_name}/{s3_key}")
        except Exception as e:
            print(f"Failed to upload {file_path_obj}: {e}")

    def upload_a_dir(self, bucket_name: str, local_folder: str, dest_folder: str = '') -> str:
        local_folder = Path(local_folder)
        if not local_folder.exists() or not local_folder.is_dir():
            print(f"Local folder does not exist or is not a directory: {local_folder}")
            return "Upload failed. Invalid folder."

        for root, _, files in os.walk(local_folder):
            for file_name in files:
                local_file_path = Path(root) / file_name
                relative_path = local_file_path.relative_to(local_folder)
                s3_key = str(Path(dest_folder) / relative_path).replace('\\', '/')

                try:
                    self.s3.upload_file(str(local_file_path), bucket_name, s3_key)
                    print(f"Uploaded: {local_file_path} to s3://{bucket_name}/{s3_key}")
                except Exception as e:
                    print(f"Failed to upload {local_file_path}: {e}")

        return "Upload completed."


_instance: S3Service = None


def get_instance() -> S3Service:
    global _instance
    if _instance is None:
        _instance = S3Service()
    return _instance


if __name__ == '__main__':
    # Example usage:
    service = get_instance()
    _bucket_name = 'dsa-evr'
    s3_folder = 'company/'
    local_dir = '/tmp/dsa/evr/'

    # Example: download a folder
    # service.download_folder(bucket_name, s3_folder, local_dir)

    # # Example: list ETags and compute a hash
    # hash_list = service.list_etag_in_folder(_bucket_name, s3_folder)
    # print(hash_list)
    # a_etag = service.get_etag(_bucket_name, "company/0ed8be99-ed68-40ed-a1df-25f077d11459/header.bin")
    # print(a_etag)
    # dir_hash = service.hash_in_folder(_bucket_name, s3_folder)
    # print(dir_hash)

    # Example: upload multiple files
    file_path_list = [
        UploadFileObj(
            dest_path="/tmp/bzk/output/chart/hash_-13362422024-11-18_23_37_24.png",
            local_path="/tmp/bzk/output/chart/hash_-13362422024-11-18_23_37_24.png"
        ),
        UploadFileObj(
            dest_path="/tmp/bzk/output/chart/hash_-362356492024-11-04_10_22_39.png",
            local_path="/tmp/bzk/output/chart/hash_-362356492024-11-04_10_22_39.png"
        ),
        UploadFileObj(
            dest_path="/tmp/bzk/output/chart/hash_397484922024-11-19_23_58_51.png",
            local_path="/tmp/bzk/output/chart/hash_397484922024-11-19_23_58_51.png"
        ),
        UploadFileObj(
            dest_path="testupload_ufo",
            local_path="/Users/kirin/Desktop/Project/dsa-rag-etl-doc-to-ver.git"
        ),
    ]

    upload_iterator: Iterator[UploadFileObj] = iter(file_path_list)
    service.upload_all(_bucket_name, upload_iterator)
    print("xxxx")

    # dirs = service.list_folders(bucket_name="dsa-doc-json", prefix="")
    # print(dirs)
    #
    # local_folder = "/Users/kirin/Desktop/Project/dsa-rag-etl-doc-to-ver.git"
    # service.upload_a_dir(bucket_name=_bucket_name, local_folder=local_folder, dest_folder="testupload")
