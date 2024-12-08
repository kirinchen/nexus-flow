from py_common_utility.utils import env_utils


def initialize(env_dir_path: str):
    print("langchain_cfg_build initialize ...")
    env_utils.load_env(env_dir_path=env_dir_path)

