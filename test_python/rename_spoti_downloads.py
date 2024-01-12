import os
import easygui
import eyed3
from mutagen.easyid3 import EasyID3

def rename_mp3s():
    p = easygui.diropenbox()
    #p = "/Users/viguri/Downloads/[SPOTIFY-DOWNLOADER.COM] Spook Factory Valencia"
    q = p + "/"
    d = os.listdir(p)
    s = "[SPOTIFY-DOWNLOADER.COM] "
    n = len(d)
    print(n)

    for x in range(n):
        old = q + d[x]
        new = q + d[x].replace(s, "")
        nom = os.rename(old, new)
        print (nom)
    
def read_id3Tiny():
    file = easygui.fileopenbox()
    tag = TinyTag.get(file)
   
    print (tag.artist)
    print (tag.album)
    print (tag.bitrate)

def read_id3():
    #https://from-locals.com/python-mutagen-mp3-id3/
    file = easygui.fileopenbox()
    tags = EasyID3(file)
    print(tags.pprint())
    
    for key in EasyID3.valid_keys.keys():
        print(key)

read_id3()
    

