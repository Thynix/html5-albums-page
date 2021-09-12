import argparse
import io
import mimetypes
import os
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape
from tinytag import TinyTag


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("page_title")
    args = parser.parse_args()

    albums = load_albums(args.path)

    env = Environment(
        loader=FileSystemLoader(os.getcwd()),
        autoescape=select_autoescape()
    )
    template = env.get_template("album.html.jinja")
    print(template.render(page_title=args.page_title, albums=albums, get_mime_type=get_mime_type))


def load_albums(path):
    # Build a list of filenames for each song. Requires that each new format of a song has the same filename with the
    # exception of its extension.
    songs = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in sorted(filenames):
            file_path = os.path.join(dirpath, filename)
            without_extension = file_path[:file_path.find(".")]
            songs[without_extension].append(file_path)

    # Find tags for each song.
    albums = defaultdict(list)
    for file_paths in songs.values():
        song_tags = None
        for file_path in sorted(file_paths, key=lambda p: {
            # OGG seems to have the most robust tag encoding.
            ".ogg": 0,
            ".mp3": 1,
            ".m4a": 2,
        }[p[p.find("."):]]):
            tags = TinyTag.get(file_path)

            # Some formats might not be tagged.
            if tags.track is None or tags.title is None or tags.artist is None or tags.album is None:
                continue

            song_tags = tags

        if song_tags is None:
            print(f"Could not find sufficient tags in any of {file_paths}")
            exit(1)

        albums[song_tags.album].append(Song(song_tags.track, song_tags.title, song_tags.artist, file_paths))

    # Sort songs within each album by track number.
    for album_name in albums.keys():
        albums[album_name] = sorted(albums[album_name], key=lambda s: s.track)

    return albums


class Song:
    def __init__(self, track: int, title: str, artist: str, file_paths: list[str]):
        self.track = track
        self.title = title
        self.artist = artist
        # Sort files for a song in order of increasing file size. (Assuming equivalent quality.)
        self.file_paths = sorted(file_paths, key=get_file_size)


def get_mime_type(file_path) -> str:
    return mimetypes.guess_type(file_path)[0]


def get_file_size(path: str) -> int:
    with open(path, 'rb') as file:
        return file.seek(0, io.SEEK_END)


if __name__ == '__main__':
    main()
