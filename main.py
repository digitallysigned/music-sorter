#!/usr/bin/env python3
import re
from pathlib import Path
from shutil import copy2
from mutagen import File
import argparse

#STORAGE_PATH = Path("/mnt/nas/music") #old
#LOOSE_DIR = STORAGE_PATH / "loose"

EXTENSIONS = {
    ".mp3", ".flac", ".wav", ".m4a"
}

def read_data(path):
    """ read data from file and return artist name """
    try:
        file_obj = File(path, easy=True)

        if file_obj is None or file_obj.tags is None:
            return None, None

        # try track artist first

        artist = file_obj.tags.get("albumartist")
        if not artist:
            artist = file_obj.tags.get("artist")
            artist = str(artist[0]).split(",", 1)[0].strip() if artist else None
            # strip artist field to only use the primary, hopefully if it is the primary lol

            # i actually prefer album artist more for sorting but its less likely to be present
            # fall back on artist anyway if not present
        else:
            artist = str(artist[0]).strip() if artist else None

        album = file_obj.tags.get("album")
        album = str(album[0]).strip() if album else None

        return artist or None, album or None

    except Exception as err:
        print(f"[ERR] Failed to read {path.name}: {err}")
        return None, None


def get_cover(path):
    """ try get embedded album cover from tags """
    try:
        file_obj = File(path, easy=False)

        format = path.suffix.lower()

        if format == ".mp3":
            cover = (file_obj.tags.getall("APIC"))[0].data
        elif format == ".flac":
            cover = (file_obj.pictures)[0].data
        elif format == ".wav":
            cover = (file_obj.tags.getall("APIC"))[0].data
        elif format == ".m4a":
            cover = bytes((file_obj.tags.get("covr"))[0])

        return cover or None

    except Exception as err:
        print(f"[ERR] Failed to read {path.name} without easy for cover: {err}")
        return None

def check_existing_cover_write(album_folder):
    """ check for existing covers in album folder, create new otherwise """
    image_exts = [ ".png", ".jpg", ".jpeg"]

    for extension in image_exts:
        path = album_folder / ("cover"+extension)
        if path.exists():
            return None

    return album_folder / "cover.jpg"


def sanitize(artist_name):
    """ make all fields the same format, basically"""
    artists = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", artist_name)
    artist = artists.strip().rstrip(". ")

    if artist in ("", ".", ".."):
        return None

    return artist

def get_folder(STORAGE_PATH, artist_name):
    """ find existing artist folder, or create a new one"""

    for folder in STORAGE_PATH.iterdir():
        if folder.is_dir() and folder.name.casefold() == artist_name.casefold():
            return folder

    folder = STORAGE_PATH / artist_name
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def get_place(folder, file_name):
    """ check that file doesnt already exists """
    path = folder / file_name

    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    i = 1

    while True:
        path = folder / f"{stem} ({i}){suffix}"

        if not path.exists():
            return path

        i += 1

def sort_music(STORAGE_PATH):
    LOOSE_DIR = STORAGE_PATH / "loose"
    if not LOOSE_DIR.is_dir():
        print(f"[ERR] Directory unfound: {LOOSE_DIR}")
        return

    files = [
        path for path in LOOSE_DIR.iterdir()
        if path.is_file() and path.suffix.lower()
           in EXTENSIONS
    ]

    if not files:
        print("No files found")
        return

    copied = 0
    skipped = 0

    for path in files:
        artist, album = read_data(path)

        if not artist:
            print(f"[SKIP] No metadata found for file: {path.name}")
            skipped += 1
            continue

        artist = sanitize(artist)
        cover = get_cover(path)

        album = sanitize(album)  if album else "Unknown Album"

        if not artist or not album:
            print(f"[SKIP] Invalid metadata for file: {path.name}")
            skipped += 1
            continue

        folder = get_folder(STORAGE_PATH, artist)
        album_folder = get_folder(folder, album)
        place = get_place(album_folder, path.name)

        try:
            if cover:
                cover_path = check_existing_cover_write(album_folder)
                if cover_path:
                    cover_path.write_bytes(cover)
            copy2(path, place)
            print(f"[COPY] {path.name} -> {artist}/{album}.")
            copied += 1

        except OSError as err:
            print(f"[ERR] Bad copy for {path.name}: {err}")
            skipped += 1

    print(f"\nFinished sorting, Copied: {copied}, skipped: {skipped}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sort files into artists folders"
    )

    parser.add_argument(
        "--storage-path",
        type=Path,
        default=Path("/mnt/nas/Music"),
        help="Specify library directory",
    )

    args = parser.parse_args()
    sort_music(args.storage_path)
