import hashlib
import os
from py_common_utility.utils import file_utils
from nexus_flow.hash.hash_info import HashInfo


def hash_result_by_path(src_uid: str, src_path: str) -> HashInfo:
    final_hash = generate_md5_by_path(src_path)
    return HashInfo(src_uid=src_uid, src_hash=final_hash)


def hash_result(src_uid: str, src_content: str) -> HashInfo:
    final_hash = generate_md5(src_content)
    return HashInfo(src_uid=src_uid, src_hash=final_hash)


def generate_md5_by_file(src_path: str, chunk_size: int = 8192) -> str:
    """
    Generate the MD5 checksum of a file.

    :param src_path: Path to the file for which the MD5 checksum is to be generated.
    :param chunk_size: Size of chunks to read from the file (default: 8192 bytes).
    :return: MD5 checksum as a hexadecimal string.
    """
    md5_hash = hashlib.md5()
    with open(src_path, 'rb') as file:
        # Read file in chunks
        for chunk in iter(lambda: file.read(chunk_size), b""):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()


def generate_md5(src_content: str) -> str:
    """
    Generate the MD5 checksum of a string.

    :param src_content: Content string to hash.
    :return: MD5 checksum as a hexadecimal string.
    """
    return hashlib.md5(src_content.encode()).hexdigest()


def generate_md5_by_dir(directory_path: str) -> str:
    """
    Generate the MD5 checksum for a directory by hashing the names and contents of its files.

    :param directory_path: Path to the directory.
    :return: MD5 checksum as a hexadecimal string.
    """
    md5_hash = hashlib.md5()

    for root, dirs, files in os.walk(directory_path):
        for name in sorted(files):  # Sort files to ensure consistent hashing order
            file_path = os.path.join(root, name)
            # Update hash with file path (relative to the directory)
            relative_path = os.path.relpath(file_path, directory_path)
            md5_hash.update(relative_path.encode())

            # Update hash with file content
            with open(file_path, 'rb') as file:
                for chunk in iter(lambda: file.read(8192), b""):
                    md5_hash.update(chunk)

    return md5_hash.hexdigest()


def generate_md5_by_path(path: str) -> str:
    """
    Generate the MD5 checksum for a file or directory.

    :param path: Path to the file or directory.
    :return: MD5 checksum as a hexadecimal string.
    """
    if os.path.isfile(path):
        return generate_md5_by_file(path)
    elif os.path.isdir(path):
        return generate_md5_by_dir(path)
    else:
        raise ValueError(f"Invalid path: {path}. It must be a file or a directory.")


if __name__ == '__main__':
    i = hash_result_by_path("foo", "/path/to/file_or_dir")
    print(i)
    i.save("/tmp/test/", "ddffccc")
