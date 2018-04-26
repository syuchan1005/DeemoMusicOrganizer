import os
import sys
import json
import shutil
from pydub import AudioSegment
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TRCK, APIC, TCON, TCMP
from mutagen.mp3 import MP3
import mutagen.id3


def WAVtoMP3(path: str):
    if path.endswith(".wav") :
        AudioSegment.from_wav(path).export(path[:-3] + "mp3", format="mp3")


def setMetaTag(filename, title, artist, album, track, track_album, pic_data):
    audio = MP3(filename, ID3=ID3)
    try:
        audio.add_tags(ID3=ID3)
    except mutagen.id3.error:
        pass
    audio["TIT2"] = TIT2(encoding=3, text=title)
    audio["TPE1"] = TPE1(encoding=3, text=artist)
    audio["TALB"] = TALB(encoding=3, text=album)
    audio['TCON'] = TCON(encoding=3, text="Deemo")
    audio["TRCK"] = TRCK(encoding=3, text=str(track) + "/" + str(track_album))
    audio["TCMP"] = TCMP(encoding=3, text="1")

    if pic_data is not None:
        audio.tags.add(
            APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc=u'Cover',
                data=pic_data
            )
        )

    audio.save()


def print_progress_bar(iteration, total, decimals=1, length=60, fill='#', nofill='-',
                       prefix='Progress:', suffix='Complate'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + nofill * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end="")
    sys.stdout.flush()
    if iteration == total:
        print()


if __name__ == "__main__":
    print("Enter the resource path")
    dirPath = input()
    if not dirPath.endswith("\\"):
        dirPath = dirPath + "\\"

    total = 0
    step = 0
    print_progress_bar(0, total=1)

    for listDir in os.listdir(dirPath):
        listPath = dirPath + listDir
        if os.path.isdir(listPath):
            os.removedirs(listPath)
        elif not (listDir.endswith(".mp3") or listDir.endswith(".wav")) or listDir.find("_pv") != -1 or os.path.getsize(listPath) < 1024000:
            os.remove(listPath)
        else:
            total += 1

    total *= 3
    total += 3
    step += 1
    print_progress_bar(step, total)

    jsonFile = open("./DeemoSongs.json", "r", encoding="utf-8")
    jsonObject = json.load(jsonFile)
    books = jsonObject["books"]
    songs = jsonObject["songs"]

    step += 1
    print_progress_bar(step, total)

    for i, v in enumerate(books):
        try:
            os.mkdir(dirPath + ("%02d" % (i + 1)) + "." + v["name"].replace(":", " "))
        except FileExistsError:
            pass

    cover = None
    if os.path.isfile("./cover.jpg"):
        cover = open("./cover.jpg", "rb").read()

    for file in os.listdir(dirPath):
        step += 1
        print_progress_bar(step, total)

        fullPath = dirPath + file
        if os.path.isdir(fullPath):
            continue
        if file[-3:] == "wav":
            WAVtoMP3(fullPath)
            os.remove(fullPath)
            fullPath = fullPath[:-3] + "mp3"

        if not (file[:-4] in songs):
            continue
        step += 1
        print_progress_bar(step, total)
        data = songs[file[:-4]]
        book = list(filter(lambda x: x["id"] == data["book"], books))[0]

        setMetaTag(fullPath, data["name"], data["artist"],("%02d" % (int(data["book"]) + 1)) + "." + book["name"], data["track"], book["track"], cover)
        shutil.move(fullPath, dirPath + ("%02d" % (books.index(book) + 1)) + "." + book["name"].replace(":", " ") + "\\" + ("%02d" % data["track"]) + ". " + data["name"] + ".mp3")
        step += 1
        print_progress_bar(step, total)
