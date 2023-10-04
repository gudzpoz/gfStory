import argparse
import os
import pathlib

from gfunpack import audio, backgrounds, characters, mapper, prefabs


parser = argparse.ArgumentParser()
parser.add_argument('dir')
parser.add_argument('-o', '--output', required=True)
args = parser.parse_args()

cpus = os.cpu_count() or 2

downloaded = args.dir
destination = pathlib.Path(args.output)

bgm = audio.BGM(downloaded, str(destination.joinpath('audio')), concurrency=cpus)
bgm.save()

images = destination.joinpath('images')
bg = backgrounds.BackgroundCollection(downloaded, str(images), pngquant=True, concurrency=cpus)
bg.save()

character_mapper = mapper.Mapper(
  prefabs.Prefabs(downloaded, str(images)),
  characters.CharacterCollection(downloaded, str(images), pngquant=True, concurrency=cpus),
)
character_mapper.write_indices()
