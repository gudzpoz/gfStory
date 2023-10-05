import argparse
import os
import pathlib

from gfunpack import audio, backgrounds, chapters, characters, mapper, prefabs, stories


parser = argparse.ArgumentParser()
parser.add_argument('dir')
parser.add_argument('-o', '--output', required=True)
parser.add_argument('--no-clean', action='store_true')
args = parser.parse_args()

cpus = os.cpu_count() or 2

downloaded = args.dir
destination = pathlib.Path(args.output)

images = destination.joinpath('images')
bg = backgrounds.BackgroundCollection(downloaded, str(images), pngquant=True, concurrency=cpus)
bg.save()

character_mapper = mapper.Mapper(
  prefabs.Prefabs(downloaded, str(images)),
  characters.CharacterCollection(downloaded, str(images), pngquant=True, concurrency=cpus),
)
character_mapper.write_indices()

bgm = audio.BGM(downloaded, str(destination.joinpath('audio')), concurrency=cpus, clean=not args.no_clean)
bgm.save()

ss = stories.Stories(downloaded, str(destination.joinpath('stories')))
ss.save()
cs = chapters.Chapters(ss)
cs.save()
