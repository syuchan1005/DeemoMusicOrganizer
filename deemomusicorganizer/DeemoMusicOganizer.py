import os
import json
import shutil
from pydub import AudioSegment
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TRCK, APIC, TDRC, TCON
from mutagen.mp3 import MP3
import mutagen.id3


def WAVtoMP3(path: str):
    if path.endswith(".wav") :
        AudioSegment.from_wav(path).export(path[:-3] + "mp3", format="mp3")


def setMetaTag(filename, title, artist, album, track, track_album):
    audio = MP3(filename, ID3=ID3)
    try:
        audio.add_tags(ID3=ID3)
    except mutagen.id3.error:
        pass
    audio["TIT2"] = TIT2(encoding=3, text=title)
    audio["TPE1"] = TPE1(encoding=3, text=artist)
    audio["TALB"] = TALB(encoding=3, text=album)
    audio['TCON'] = TCON(encoding=3, text="Deemo")
    audio["TRCK"] = TRCK(encoding=3, text=[(track, track_album)])
    audio.save()


if __name__ == "__main__":
    print("Enter the resource path")
    dirPath = input()
    if not dirPath.endswith("\\"):
        dirPath = dirPath + "\\"

    for list in os.listdir(dirPath):
        listPath = dirPath + list
        if os.path.isdir(listPath):
            os.removedirs(listPath)
        elif not (list.endswith(".mp3") or list.endswith(".wav")) or os.path.getsize(listPath) < 1024000 or list.find("_pv") != -1:
            os.remove(listPath)

    jsonFile = open("./DeemoSongs.json", "r", encoding="utf-8")
    jsonObject = json.load(jsonFile)
    books = jsonObject["books"]
    songs = jsonObject["songs"]

    for i, v in enumerate(books):
        try:
            os.mkdir(dirPath + v["name"].replace(":", " "))
        except FileExistsError:
            pass

    for file in os.listdir(dirPath):
        fullPath = dirPath + file
        if os.path.isdir(fullPath):
            continue
        if file[-3:] == "wav":
            WAVtoMP3(fullPath)
            os.remove(fullPath)
            fullPath = fullPath[:-3] + "mp3"
        data = songs[file[:-4]]
        book = books[data["book"]]
        setMetaTag(fullPath, data["name"], data["artist"], book["name"], data["track"], book["track"])
        shutil.move(fullPath, dirPath + book["name"].replace(":", " ") + "\\" + ("%02d" % data["track"]) + ". " + data["name"] + ".mp3")
