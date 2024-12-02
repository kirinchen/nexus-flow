import json
import os.path
from dataclasses import dataclass
from typing import Optional

from py_common_utility.utils import file_utils, time_utils

from nexus_flow.infra import nexus_flow_constant


@dataclass
class HashInfo:
    src_uid: str
    src_hash: str
    dest_hash: Optional[str] = None
    check_at: Optional[str] = None  # datetime iso8601 format

    def save(self, orig_file_path: str, dest_hash: str) -> str:
        self.dest_hash = dest_hash
        _now = time_utils.get_ntc_now()
        self.check_at = _now.isoformat()
        jstr = json.dumps(self.__dict__, indent=2)
        path = orig_file_path + nexus_flow_constant.HASH_INFO_EXTENSION
        file_utils.ensure_directory_exists(orig_file_path)
        file_utils.save_string_to_file(path, jstr)
        return path
