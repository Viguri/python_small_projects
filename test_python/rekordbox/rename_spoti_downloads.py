import os
import easygui
import eyed3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.aiff import AIFF


def rename_mp3s():
    p = easygui.diropenbox()
    #p = "G:/__DJ-ING/__NEW_RELEASES/New/New Exclusive Music – 144 Tracks Сollection March 2024 (Djsoundtop.Com)"
    q = p + "/"
    d = os.listdir(p)
    text = input("inserta texto a eliminar: ")
    t = print(text)

    #s = "OG KAALA - "
    s = text
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
    try:
        file = easygui.fileopenbox()
        tags = ID3(file)
    except ID3NoHeaderError:
        tags = ID3()    
    
    tags = EasyID3(file)
    print(tags.pprint())
    
    for key in EasyID3.valid_keys.keys():
        print(key)

#read_id3()
rename_mp3s()
    

