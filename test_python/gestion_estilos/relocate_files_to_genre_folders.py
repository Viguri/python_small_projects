import os
import shutil
import eyed3
import mutagen
from mutagen.flac import FLAC
from datetime import datetime
from tkinter import Tk, filedialog
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
import json
import queue
import difflib

MAX_PATH_LENGTH = 260
MAX_FOLDER_NAME_LENGTH = 100
MAX_FILE_NAME_LENGTH = 100
GENRE_MAPPING_FILE = "genre_mapping.json"
DB_FILE = "music_metadata.db"
BATCH_SIZE = 100
SIMILARITY_THRESHOLD = 0.6  # Umbral de similitud para agrupar géneros

# Función para cargar el mapeo de géneros desde un archivo JSON
def load_genre_mapping(file_path=GENRE_MAPPING_FILE):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

# Función para guardar el mapeo de géneros en un archivo JSON
def save_genre_mapping(genre_mapping, file_path=GENRE_MAPPING_FILE):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(genre_mapping, f, ensure_ascii=False, indent=4)

# Función para sanitizar nombres de géneros
def sanitize_genre(genre):
    sanitized_genre = re.sub(r'[^A-Za-z0-9 ]+', '', genre)
    sanitized_genre = re.sub(r'\s+', ' ', sanitized_genre)
    return sanitized_genre.strip()

# Función para sanitizar nombres de archivo
def sanitize_file_name(file_name):
    sanitized_file_name = re.sub(r'[<>:"/\\|?*]', '', file_name)
    sanitized_file_name = re.sub(r'[&,()]', '', sanitized_file_name)
    sanitized_file_name = re.sub(r'\s+', ' ', sanitized_file_name)
    return sanitized_file_name.strip()

# Función para truncar nombres de carpetas
def truncate_folder_name(folder_name, max_length=MAX_FOLDER_NAME_LENGTH):
    if len(folder_name) > max_length:
        return folder_name[:max_length].rstrip()
    return folder_name

# Función para truncar una ruta si excede la longitud máxima permitida
def truncate_path(path, max_length=MAX_PATH_LENGTH):
    if len(path) > max_length:
        return path[:max_length].rstrip()
    return path

# Función para leer el género de archivos FLAC y otros formatos usando mutagen
def read_genre_with_mutagen(file_path):
    try:
        if file_path.lower().endswith('.flac'):
            audio = FLAC(file_path)
            if 'genre' in audio:
                return audio['genre'][0]
            else:
                print(f"El archivo FLAC {file_path} no tiene una etiqueta de género.")
        else:
            audio = mutagen.File(file_path, easy=True)
            if audio and 'genre' in audio:
                return audio['genre'][0]
    except Exception as e:
        print(f"Error al leer el género de {file_path}: {e}")
    return None

# Función para leer el género usando mutagen o eyed3 para archivos MP3
def read_genre(file_path):
    genre = read_genre_with_mutagen(file_path)
    if genre:
        return genre

    if file_path.lower().endswith('.mp3'):
        try:
            audio = eyed3.load(file_path)
            if audio and audio.tag and audio.tag.genre:
                return audio.tag.genre.name
        except Exception as e:
            print(f"Error al leer el género de {file_path} (MP3 con eyed3): {e}")
    
    return None

# Algoritmo para agrupar géneros basados en similitud
def group_similar_genres(genres):
    grouped_genres = {}

    for genre in genres:
        found_group = False
        for group in grouped_genres:
            # Usamos SequenceMatcher para determinar si los géneros son suficientemente similares
            if difflib.SequenceMatcher(None, genre, group).ratio() > SIMILARITY_THRESHOLD:
                grouped_genres[group].append(genre)
                found_group = True
                break
        if not found_group:
            grouped_genres[genre] = [genre]

    return grouped_genres

# Función para mapear un género a su categoría principal
def map_genre_to_category(genre, genre_mapping):
    for main_genre, sub_genres in genre_mapping.items():
        for sub_genre in sub_genres:
            if sub_genre.lower() == genre.lower():
                return main_genre  # Devuelve la categoría principal si se encuentra una coincidencia
    return 'Other'

# Función para crear carpetas de géneros
def create_genre_folders(destination_dir, genre_mapping):
    for main_genre, sub_genres in genre_mapping.items():
        main_genre_sanitized = truncate_folder_name(sanitize_genre(main_genre))
        main_genre_folder = os.path.join(destination_dir, main_genre_sanitized)
        os.makedirs(main_genre_folder, exist_ok=True)

        for sub_genre in sub_genres:
            sub_genre_sanitized = truncate_folder_name(sanitize_genre(sub_genre))
            sub_genre_folder = os.path.join(main_genre_folder, sub_genre_sanitized)
            sub_genre_folder = truncate_path(sub_genre_folder)
            try:
                os.makedirs(sub_genre_folder, exist_ok=True)
            except FileNotFoundError as e:
                print(f"Error al crear el directorio {sub_genre_folder}: {e}")

# Función para copiar archivos a las carpetas de géneros correspondientes
def copy_files_to_folders(files_dir, destination_dir, genre_mapping):
    files_copied = 0
    supported_formats = ['.mp3', '.flac', '.ogg', '.wav', '.m4a']
    files = []

    # Recolecta todos los archivos
    for root, _, filenames in os.walk(files_dir):
        for file in filenames:
            file_path = os.path.join(root, file)
            if any(file.lower().endswith(fmt) for fmt in supported_formats):
                files.append(file_path)

    # Copia archivos en paralelo
    def copy_file(file_path):
        try:
            genre = read_genre(file_path)
            if genre:
                genre_sanitized = sanitize_genre(genre)
                main_genre = map_genre_to_category(genre, genre_mapping)
                if main_genre:
                    main_genre_sanitized = sanitize_genre(main_genre)
                    destination_folder = os.path.join(destination_dir, main_genre_sanitized, genre_sanitized)
                    os.makedirs(destination_folder, exist_ok=True)

                    file_name = os.path.basename(file_path)
                    sanitized_file_name = sanitize_file_name(file_name)
                    sanitized_file_name = sanitized_file_name[:MAX_FILE_NAME_LENGTH].rstrip()

                    destination_file_path = os.path.join(destination_folder, sanitized_file_name)
                    destination_file_path = truncate_path(destination_file_path)

                    if not os.path.exists(destination_file_path):
                        try:
                            shutil.copy2(file_path, destination_file_path)
                            print(f"Copiado {sanitized_file_name} a {destination_folder}")
                            return 1
                        except FileNotFoundError as e:
                            print(f"Error al copiar el archivo {sanitized_file_name}: {e}")
                    else:
                        print(f"El archivo {sanitized_file_name} ya existe en {destination_folder}, omitiendo la copia.")
                else:
                    print(f"Género {genre} no encontrado en el mapeo. Omitiendo archivo.")
            else:
                print(f"Omitiendo el archivo {os.path.basename(file_path)} porque no se pudo extraer el género.")
        except FileNotFoundError as e:
            print(f"Error al procesar el archivo {file_path}: {e}. Saltando al siguiente archivo.")
        except Exception as e:
            print(f"Error inesperado al procesar el archivo {file_path}: {e}. Saltando al siguiente archivo.")
        return 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(copy_file, file_path) for file_path in files]
        for future in as_completed(futures):
            files_copied += future.result()

    return files_copied

# Función para escanear archivos y recolectar géneros
def scan_files_for_genres_and_metadata(directory):
    new_genres = set()
    metadata_queue = queue.Queue()
    files = []

    # Recolecta todos los archivos
    for root, _, filenames in os.walk(directory):
        for file in filenames:
            file_path = os.path.join(root, file)
            files.append(file_path)

    # Procesa archivos en paralelo
    def process_file(file_path, metadata_queue):
        try:
            genre = read_genre(file_path)
            genre_cleaned = sanitize_genre(genre) if genre else None

            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()

            # Intentamos obtener la fecha de modificación del archivo
            try:
                date_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            except FileNotFoundError as e:
                print(f"Error al obtener la fecha de modificación: {e}. Archivo omitido.")
                return None

            # Guardamos el archivo procesado en la cola de metadatos
            record = (file_name, file_extension, genre_cleaned, file_path, date_modified)
            metadata_queue.put(record)

            return genre_cleaned

        except Exception as e:
            print(f"Error al procesar el archivo {file_path}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_file, file_path, metadata_queue) for file_path in files]
        for future in as_completed(futures):
            genre_cleaned = future.result()
            if genre_cleaned:
                new_genres.add(genre_cleaned)

    return new_genres

# Función para actualizar el mapeo de géneros
def update_genre_mapping(new_genres, genre_mapping):
    updated = False
    for new_genre in new_genres:
        found = False
        for main_genre, sub_genres in genre_mapping.items():
            if any(new_genre.lower() == sub_genre.lower() for sub_genre in sub_genres):
                found = True
                break
        if not found:
            if 'Other' not in genre_mapping:
                genre_mapping['Other'] = []
            if new_genre not in genre_mapping['Other']:
                genre_mapping['Other'].append(new_genre)
                updated = True
                print(f"Nuevo género añadido: {new_genre}")

    return updated

# Función para crear la base de datos y la tabla para los metadatos
def create_db(db_file=DB_FILE):
    conn = sqlite3.connect(db_file, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS music_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_extension TEXT NOT NULL,
            genre TEXT,
            file_path TEXT NOT NULL,
            date_modified TEXT
        )
    ''')
    conn.commit()
    return conn

# Función principal
def main():
    genre_mapping = load_genre_mapping()

    root = Tk()
    root.withdraw()
    new_files_dir = filedialog.askdirectory(title="Selecciona la carpeta con los nuevos archivos de música")

    if not new_files_dir:
        print("Operación cancelada.")
        return

    destination_dir = filedialog.askdirectory(title="Selecciona la carpeta de destino para los archivos de música organizados")

    if not destination_dir:
        print("Operación cancelada.")
        return

    conn = create_db()
    conn.close()

    new_genres = scan_files_for_genres_and_metadata(new_files_dir)

    if not new_genres:
        print("No se encontraron nuevos géneros.")
        return

    updated = update_genre_mapping(new_genres, genre_mapping)

    if updated:
        save_genre_mapping(genre_mapping)
        print("El mapeo de géneros ha sido actualizado.")
    else:
        print("No se añadieron nuevos géneros al mapeo.")

    # Agrupación de géneros similares antes de crear las carpetas
    genre_mapping = group_similar_genres(new_genres)

    create_genre_folders(destination_dir, genre_mapping)

    # Confirmar antes de copiar los archivos
    proceed = input("¿Deseas proceder a copiar los archivos a la nueva estructura de carpetas? (y/n): ")
    if proceed.lower() != 'y':
        print("Operación cancelada antes de copiar los archivos.")
        return

    files_copied = copy_files_to_folders(new_files_dir, destination_dir, genre_mapping)
    print(f"Se copiaron {files_copied} archivos a la nueva estructura de carpetas.")

if __name__ == "__main__":
    main()
