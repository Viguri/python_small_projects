import os
import logging
from collections import defaultdict
from tabulate import tabulate
from pyrekordbox import Rekordbox6Database
from pyrekordbox.db6 import tables
import html

# Set up logging
logging.basicConfig(level=logging.INFO)

# Camelot Wheel for Harmonic Mixing
camelot_wheel = {
    "1A": ["12A", "2A", "1B"], "2A": ["1A", "3A", "2B"], "3A": ["2A", "4A", "3B"],
    "4A": ["3A", "5A", "4B"], "5A": ["4A", "6A", "5B"], "6A": ["5A", "7A", "6B"],
    "7A": ["6A", "8A", "7B"], "8A": ["7A", "9A", "8B"], "9A": ["8A", "10A", "9B"],
    "10A": ["9A", "11A", "10B"], "11A": ["10A", "12A", "11B"], "12A": ["11A", "1A", "12B"],
    "1B": ["1A", "12B", "2B"], "2B": ["2A", "1B", "3B"], "3B": ["3A", "2B", "4B"],
    "4B": ["4A", "3B", "5B"], "5B": ["5A", "4B", "6B"], "6B": ["6A", "5B", "7B"],
    "7B": ["7A", "6B", "8B"], "8B": ["8A", "7B", "9B"], "9B": ["9A", "8B", "10B"],
    "10B": ["10A", "9B", "11B"], "11B": ["11A", "10B", "12B"], "12B": ["12A", "11B", "1B"]
}

# Function to retrieve tracks from Rekordbox 6
def get_tracks_from_rekordbox6(dropbox_path, follow_camelot):
    try:
        db = Rekordbox6Database()
    except Exception as e:
        logging.error(f"Error accessing Rekordbox database: {e}")
        return []

    playlist_tracks = []
    album_track_count = defaultdict(int)

    for content in db.get_content():
        cont = db.query(tables.DjmdContent)
        keys = db.query(tables.DjmdKey)
        
        album_name = content.Album if content.Album else "Unknown Album"

        # Skip albums with more than 2 tracks already selected
        if album_track_count[album_name] >= 2:
            continue

        # Correct the file location access (using content.Path)
        path = content.FolderPath
        if path is None:
            #logging.info(f"Skipping track {content.Title} due to missing folder path.")
            continue        
        else:
            file_path = os.path.join(dropbox_path, *path.split("/"))

        # Filter harmonic mixing by Camelot Wheel if required
        keyName = cont.filter(cont.KeyID == keys.KeyID).first()
        print("keyName: " + keyName)
        
        if content.KeyID is not None:
            if content.KeyID == tables.DjmdContent.KeyID:
                print(keyName)
            else:
                keyName = None
        
        if follow_camelot and (content.KeyID is None or keyName not in camelot_wheel):
            logging.info(f"Skipping track {content.Title} due to invalid Camelot Wheel key: {keyName}")
            continue

        playlist_tracks.append({
            "track_name": content.Title,
            "artist": content.Artist.Name,
            "album": album_name,
            "duration": content.Duration,
            "duration_formatted": f"{content.Duration // 60}:{content.Duration % 60:02d}",
            "key": content.Key,
            "file_path": file_path
        })

        # Track the number of selected tracks per album
        album_track_count[album_name] += 1

    logging.info(f"{len(playlist_tracks)} tracks retrieved from Rekordbox.")
    return playlist_tracks

# Function to divide the playlist into phases (Intro, Development, Final)
def divide_into_phases(tracks, phase_durations):
    intro_tracks, dev_tracks, final_tracks = [], [], []
    current_duration = 0
    for track in tracks:
        current_duration += track["duration"]
        if current_duration >= sum(phase_durations.values()):
            break
        if current_duration <= phase_durations["intro"]:
            intro_tracks.append(track)
        elif current_duration <= phase_durations["intro"] + phase_durations["development"]:
            dev_tracks.append(track)
        else:
            final_tracks.append(track)
    return intro_tracks, dev_tracks, final_tracks

# Function to write the .m3u file
def export_to_m3u(tracks, export_path):
    if not tracks:
        logging.warning("No tracks to export to .m3u file.")
        return

    try:
        with open(export_path, "w") as m3u_file:
            m3u_file.write("#EXTM3U\n")
            for track in tracks:
                m3u_file.write(html.escape(f"#EXTINF:{track['duration_formatted']},{track['artist']} - {track['track_name']}\n"))
                m3u_file.write(f"{html.escape(track['file_path'])}\n")
        logging.info(f"Playlist successfully exported to {export_path}")
    except Exception as e:
        logging.error(f"Error exporting playlist: {e}")

# Function to print the tracklist table
def print_table(tracks):
    table = [[t.get('track_name', 'Unknown'), t.get('artist', 'Unknown'), t.get('album', 'Unknown'),
              t.get('duration_formatted', '00:00'), t.get('key', 'Unknown')] for t in tracks]
    headers = ["Track Name", "Artist", "Album", "Duration (MM:SS)", "Key"]
    print(tabulate(table, headers, tablefmt="fancy_grid"))

# Main function with interactive terminal input
def main():
    # Default values
    default_dropbox_path = os.getenv("DROPBOX_PATH", "D:/__CLOUD/__DROPBOX/Professional DJ team Dropbox/Manuel Viguri/")
    default_min_duration = 70
    default_camelot = "yes"
    default_phases = 3
    default_export_path = "final_playlist.m3u"

    # Interactive input, with default values if input is empty
    dropbox_path = input(f"Enter your Dropbox path (default: {default_dropbox_path}): ").strip() or default_dropbox_path
    min_duration = input(f"Enter the minimum session duration in minutes (default: {default_min_duration}): ").strip() or default_min_duration
    try:
        min_duration = int(min_duration)
    except ValueError:
        logging.error("Invalid input for session duration.")
        return

    use_camelot = input(f"Should the playlist follow Camelot Wheel harmonic mixing? (yes/no, default: {default_camelot}): ").strip() or default_camelot
    use_camelot = use_camelot.lower() == "yes"

    phases = input(f"How many phases should the session have? (1=Full, 2=Intro/Dev, 3=Intro/Dev/Final, default: {default_phases}): ").strip() or default_phases
    try:
        phases = int(phases)
    except ValueError:
        logging.error("Invalid input for phases.")
        return

    export_path = input(f"Enter the export path for the .m3u file (default: {default_export_path}): ").strip() or default_export_path

    # Define session duration in seconds and phase structure
    total_duration_sec = min_duration * 60
    if phases == 3:
        phase_durations = {"intro": round(total_duration_sec * 0.2), "development": round(total_duration_sec * 0.6), "final": round(total_duration_sec * 0.2)}
    elif phases == 2:
        phase_durations = {"intro": round(total_duration_sec * 0.4), "development": round(total_duration_sec * 0.6), "final": 0}
    else:
        phase_durations = {"intro": total_duration_sec, "development": 0, "final": 0}

    # Fetch tracks from Rekordbox 6 database
    tracks = get_tracks_from_rekordbox6(dropbox_path, use_camelot)
    if not tracks:
        logging.warning("No tracks available for the playlist.")
        return

    # Divide tracks into phases
    intro_tracks, dev_tracks, final_tracks = divide_into_phases(tracks, phase_durations)

    # Print the table for each phase
    print("\nIntro Phase:")
    print_table(intro_tracks)
    print("\nDevelopment Phase:")
    print_table(dev_tracks)
    if final_tracks:
        print("\nFinal Phase:")
        print_table(final_tracks)

    # Export tracks to an m3u file
    all_tracks = intro_tracks + dev_tracks + final_tracks
    export_to_m3u(all_tracks, export_path)

if __name__ == "__main__":
    main()
