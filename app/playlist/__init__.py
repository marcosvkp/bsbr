from dataclasses import dataclass
from typing import List


@dataclass
class Difficulty:
    characteristic: str
    name: str


@dataclass
class Song:
    songName: str
    levelAuthorName: str
    hash: str
    difficulties: List[Difficulty]


@dataclass
class CustomData:
    syncURL: str


@dataclass
class Playlist:
    playlistTitle: str
    playlistAuthor: str
    customData: CustomData
    songs: List[Song]
    image: str
