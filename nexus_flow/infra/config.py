import argparse
import os

from dotenv import load_dotenv


_inited = False


def load_env(env_dir_path: str):
    global _inited
    if _inited:
        return
    _inited = True
    load_dotenv()
    load_dotenv(verbose=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", help="environment")
    args = parser.parse_args()
    env_text = args.env if args.env else ''
    env_path = os.path.join(env_dir_path, f'{env_text}.env')
    load_dotenv(dotenv_path=env_path, override=True)


def env(s) -> str:
    return os.getenv(s)


def env_int(s) -> int:
    return int(os.getenv(s))


def env_float(s) -> float:
    return float(os.getenv(s))


def env_bool(s) -> bool:
    return env(s) == 'true'


if __name__ == '__main__':
    print(env('db_port'))
