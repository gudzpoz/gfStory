import pathlib
import subprocess
import threading
import zipfile

import tqdm

from gfunpack import utils


def _test_vgmstream():
    try:
        subprocess.run([
            'vgmstream-cli',
            '-V',
        ], stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        raise FileNotFoundError('vgmstream-cli is required to unpack sound files')


def _extract_zip(path: pathlib.Path, directory: pathlib.Path):
    with zipfile.ZipFile(path) as z:
        z.extractall(directory)
        return [directory.joinpath(file.filename) for file in z.filelist]


def _test_ffmpeg():
    try:
        subprocess.run([
            'ffmpeg',
            '-h',
        ], stdout=subprocess.DEVNULL).check_returncode()
    except FileNotFoundError:
        raise FileNotFoundError('ffmpeg is required to transcode audio files')
    

def _transcode_files(files: list[pathlib.Path], force: bool, concurrency: int):
    _test_ffmpeg()
    semaphore = threading.Semaphore(concurrency)
    def transcode(file: pathlib.Path, output: pathlib.Path):
        nonlocal force, semaphore
        if force or not output.is_file():
            subprocess.run([
                'ffmpeg',
                '-hide_banner',
                '-loglevel',
                'error',
                '-i',
                file,
                output,
            ]).check_returncode()
        semaphore.release()

    converted: dict[str, pathlib.Path] = {}
    for file in tqdm.tqdm(files):
        semaphore.acquire()
        output = file.with_suffix('.m4a')
        threading.Thread(target=transcode, args=(file, output)).start()
        converted[file.stem] = output

    for _ in range(concurrency):
        semaphore.acquire()
    return converted


def _extract_acb_to_wav(dat: pathlib.Path, destination: pathlib.Path, semaphore: threading.Semaphore | None = None):
    acb_audios = _extract_zip(dat, destination)
    assert len(acb_audios) == 1
    acb = acb_audios[0]
    assert acb.suffix == '.bytes'
    acb = acb.rename(acb.with_suffix(''))
    subprocess.run([
        'vgmstream-cli',
        acb,
        '-o',
        destination.joinpath('?n.wav'),
        '-S',
        '0',
    ]).check_returncode()
    acb.unlink()
    if semaphore is not None:
        semaphore.release()
    return acb


class SoundEffects:
    directory: pathlib.Path

    destination: pathlib.Path

    resource_file: pathlib.Path

    extracted: dict[str, pathlib.Path]

    force: bool

    concurrency: int

    def __init__(self, directory: str, destination: str, force: bool = False, concurrency: int = 8) -> None:
        self.directory = utils.check_directory(directory)
        self.destination = utils.check_directory(pathlib.Path(destination).joinpath('se'), create=True)
        self.force = force
        self.concurrency = concurrency
        self.resource_file = list(self.directory.glob('*AVGacb3030.dat'))[0]
        self.extracted = self.extract_and_convert()

    def extract_all(self):
        _test_vgmstream()
        _extract_acb_to_wav(self.resource_file, self.destination)
        return list(self.destination.glob('*.wav'))

    def extract_and_convert(self):
        return _transcode_files(self.extract_all(), self.force, self.concurrency)

class BGM:
    directory: pathlib.Path

    destination: pathlib.Path

    resource_files: list[pathlib.Path]

    extracted: dict[str, pathlib.Path]

    force: bool

    concurrency: int

    def __init__(self, directory: str, destination: str, force: bool = False, concurrency: int = 8) -> None:
        self.directory = utils.check_directory(directory)
        self.destination = utils.check_directory(pathlib.Path(destination).joinpath('bgm'), create=True)
        self.force = force
        self.concurrency = concurrency
        self.resource_files = list(f for f in self.directory.glob('*acb3030.dat') if 'AVGacb3030' not in f.stem)
        self.extracted = self.extract_and_convert()

    def extract_all(self):
        _test_vgmstream()
        semaphore = threading.Semaphore(self.concurrency)
        for file in self.resource_files:
            semaphore.acquire()
            threading.Thread(target=_extract_acb_to_wav, args=(file, self.destination, semaphore)).start()
        for _ in range(self.concurrency):
            semaphore.acquire()
        return list(self.destination.glob('*.wav'))

    def extract_and_convert(self):
        return _transcode_files(self.extract_all(), self.force, self.concurrency)
