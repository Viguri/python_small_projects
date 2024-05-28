from pyrekordbox import show_config
from pyrekordbox import Rekordbox6Database
from pyrekordbox.db6 import tables

show_config()

db = Rekordbox6Database()

query = db.query(tables.DjmdContent)
results = query.count(tables.DjmdContent.Genre)

for content in db.get_content():
    print(content.Title, content.Artist.Name)

playlist = db.get_playlist()[1]
print(playlist)

""" for song in playlist.Songs:
    content = song.Content
    print(content.Title, content.Artist.Name) """