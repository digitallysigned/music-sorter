# vi's super cool music sorter

I made this out of boredom and an annoyance at how annoying it was to sort new music on my nas, its specifically fit to work for me so grain of salt

----

## Features:

 - Metadata based artist and album sorting
 - Album cover extraction
 - Duplicate detection

## Requirements:

- python 3 (duh)
- Mutagen

## Usage:

Clone the tool:

```
git clone https://github.com/digitallysigned/music-sorter
cd music-sorter
```

You can choose to use the default music library path if it fits your own setup `/mnt/nas/Music/`, but likely this isnt the case so you can specify a specific path when running the tool:

```py
python3 sorter.py --storage-path="/wherever/you/want/Music"
```

**Note: The sorter excepts a certain directory structure to be able to function properly, see below**

## Structure

Unsorted music should be placed into a folder named `loose`, as seen below:

```
Music/
└── loose/
  ├── song1.flac
  └── song2.wav
```

This will generate a sort like this:
```
Music/
├── loose/
│ ├── song1.flac
│ └── song2.wav
└── Artist/
  └── Album/
    ├── song1.flac
    ├── song2.wav
    └── cover.jpg  
```

The original unsorted files remain in the loose folder, and should be deleted manually afterwards, as long as sorting was correct

## Support and Limitations

The only supported formats for audio are:

- .WAV
- .FLAC
- .MP3
- .M4A

Any other formats will not work, however adding them to the list of expected extensions in the script might work with the exception of cover art fetching which requires specific instructions.

### Cover fetching

Covers are expected to come directly from the audio files tags, and will not seek out a existing `cover` image file alongside it (except in the destination folder to negate duplicates) 

