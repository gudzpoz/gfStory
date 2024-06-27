import dataclasses
import json

from gfunpack import prefabs


def test_collecting_files():
    info = prefabs.Prefabs('downloader/output')
    with open('prefabs.json', 'w') as f:
        json.dump(
            dict((k, [dataclasses.asdict(i) for i in v]) for k, v in info.details.items()),
            f,
            indent=2,
        )


if __name__ == '__main__':
    test_collecting_files()
