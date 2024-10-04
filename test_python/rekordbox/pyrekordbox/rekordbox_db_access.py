from pyrekordbox import Rekordbox6Database
from pyrekordbox import show_config
from pyrekordbox.db6 import tables

show_config()

db = Rekordbox6Database()

query = db.query(tables.DjmdContent)
results = query.count()  # Removed the argument

# Limit the loop to 10 occurrences and check for NoneType
for i, content in enumerate(db.get_content()):
    if content.Artist is not None:
        print(content.Title, content.Artist.Name)
    else:
        print(content.Title, "Unknown Artist")

playlist = db.get_playlist()[1]
print(playlist)

# Uncomment and add error handling for the playlist songs if needed
# for song in playlist.Songs:
#     content = song.Content
#     if content.Artist is not None:
#         print(content.Title, content.Artist.Name)
#     else:
#         print(content.Title, "Unknown Artist")