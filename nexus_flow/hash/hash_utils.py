import hashlib

from py_common_utility.utils import file_utils

from nexus_flow.hash.hash_info import HashInfo


def hash_result_by_path(src_uid: str, src_path: str) -> HashInfo:
    final_hash = generate_md5_by_file(src_path)
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
    final_hash = hashlib.md5(src_content.encode()).hexdigest()
    return final_hash


if __name__ == '__main__':
    i = hash_result("foo", "bar")
    print(i)
    i.save("/tmp/test/", "ddffccc")
