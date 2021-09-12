from tinytag import TinyTag
import argparse
import os
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader, select_autoescape
import mimetypes


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
        for file_path in file_paths:
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
        self.file_paths = file_paths


def get_mime_type(file_path):
    return mimetypes.guess_type(file_path)[0]


if __name__ == '__main__':
    main()
