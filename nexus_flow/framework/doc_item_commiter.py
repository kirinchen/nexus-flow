import json
import os
from dataclasses import dataclass
from typing import Iterator, List, Callable

from py_common_utility.utils import env_utils

from nexus_flow.hash import hash_utils
from nexus_flow.hash.hash_info import HashInfo
from nexus_flow.infra import nexus_flow_constant
from nexus_flow.s3 import s3_service
from nexus_flow.s3.s3_service import UploadFileObj


@dataclass
class UploadDocItem:
    repo_key: str
    file_path: str
    src_hash: str


@dataclass
class SyncDocItem:
    repo_key: str
    src_hash: str
    content_provide: Callable[[str], str]


def _to_upload_file_iterator(doc_iterator: Iterator[UploadDocItem]) -> Iterator[UploadFileObj]:
    for doc in doc_iterator:
        yield UploadFileObj(
            dest_path=f"{doc.repo_key}",
            local_path=doc.file_path
        )
        dest_hash = hash_utils.generate_md5_by_file(doc.file_path)
        dest_hash_info: HashInfo = HashInfo(src_uid=doc.repo_key, src_hash=doc.src_hash)
        hash_file_path = dest_hash_info.save(doc.file_path, dest_hash)
        yield UploadFileObj(
            dest_path=f"{doc.repo_key}{nexus_flow_constant.HASH_INFO_EXTENSION}",
            local_path=hash_file_path
        )


class DocItemCommiter:

    def __init__(self, bucket_name: str, s3_folder: str, local_dir: str):
        self.bucket_name: str = bucket_name
        self.s3_folder: str = s3_folder
        self.local_dir: str = local_dir
        self.repo_tag_list: List[dict] = s3_service.get_instance().list_etag_in_folder(bucket_name=self.bucket_name,
                                                                      folder_prefix=self.s3_folder,
                                                                      file_extensions=[
                                                                          nexus_flow_constant.HASH_INFO_EXTENSION])

    def _mark_tag(self, key: str):
        _key = key + nexus_flow_constant.HASH_INFO_EXTENSION
        self.repo_tag_list = [i for i in self.repo_tag_list if i.get('Key') != _key]

    def is_up_to_date(self, item: SyncDocItem) -> bool:
        hash_json: str = s3_service.get_instance().get_file_content(self.bucket_name,
                                                   s3_key=item.repo_key + nexus_flow_constant.HASH_INFO_EXTENSION)
        if not hash_json:
            return False
        hash_obj = json.loads(hash_json)
        src_hash = hash_obj.get('src_hash')
        return src_hash == item.src_hash

    def commit(self, items: Iterator[SyncDocItem]):
        _upload_file_iterator = self.commit_push_files(items)
        self.append_doc_all(_upload_file_iterator)

    def commit_push_files(self, items: Iterator[SyncDocItem]) -> Iterator[UploadDocItem]:
        for item in items:
            if self.is_up_to_date(item):
                self._mark_tag(item.repo_key)
                continue
            new_content_item_path: str = item.content_provide(item.repo_key)
            yield UploadDocItem(repo_key=item.repo_key, file_path=new_content_item_path, src_hash=item.src_hash)
        for rm_tag in self.repo_tag_list:
            _key: str = rm_tag['Key']
            s3_service.get_instance().delete_file(self.bucket_name, _key)
            orig_key = _key.removesuffix(nexus_flow_constant.HASH_INFO_EXTENSION)
            s3_service.get_instance().delete_file(self.bucket_name, orig_key)

    def append_doc_all(self, doc_iterator: Iterator[UploadDocItem]):
        file_list_it = _to_upload_file_iterator(doc_iterator)
        s3_service.get_instance().upload_all(self.bucket_name, file_list_it)


if __name__ == '__main__':
    from nexus_flow import nexus_flow_app
    wd_path = os.path.dirname(__file__)
    wd_path = os.path.dirname(wd_path)
    wd_path = os.path.dirname(wd_path)
    print(wd_path)
    nexus_flow_app.initialize(wd_path)
    print(env_utils.env('AWS_ACCESS_KEY_ID'))
    commiter = DocItemCommiter(bucket_name="dsa-doc-json", s3_folder="test/", local_dir="/tmp/dsa-doc-json/test/")
    # new_doc_list = [
    #     UploadDocItem(repo_key="test/djson/1.png",
    #                   file_path="/tmp/bzk/output/chart/hash_-13362422024-11-18_23_37_24.png",
    #                   src_hash="1234567890abcdef"),
    #     UploadDocItem(repo_key="test/djson/2.png",
    #                   file_path="/tmp/bzk/output/chart/hash_-362356492024-11-04_10_22_39.png",
    #                   src_hash="fedcba9876543210"),
    #     UploadDocItem(repo_key="test/djson/3.png",
    #                   file_path="/tmp/bzk/output/chart/hash_397484922024-11-19_23_58_51.png",
    #                   src_hash="0987654321fedcba"),
    # ]
    # new_doc_list_it = iter(new_doc_list)
    # commiter.append_doc_all(new_doc_list_it)
    commiter.commit(iter([
        SyncDocItem(
            repo_key="test/djson/1.png",
            src_hash="1234567890abcdef",
            content_provide=lambda repo_key: "/tmp/bzk/output/chart/hash_-13362422024-11-18_23_37_24.png"
        ),
        SyncDocItem(
            repo_key="test/djson/2.png",
            src_hash="fedcba9876543210",
            content_provide=lambda repo_key: "/tmp/bzk/output/chart/hash_-362356492024-11-04_10_22_39.png"
        )

    ]))
    print("DONE~~~~~~~~~~~~~~~~")
