from nexus_flow.infra import config


def initialize(env_dir_path: str):
    print("langchain_cfg_build initialize ...")
    config.load_env(env_dir_path=env_dir_path)

