import os
import shutil
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def copy_file(file_path: Path, target_root: Path):
    if file_path.is_file():
        ext = file_path.suffix.lower().lstrip(".")
        if not ext:
            return
        target_dir = target_root / ext
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, target_dir / file_path.name)

def process_directory(directory: Path, target_root: Path, executor: ThreadPoolExecutor, futures: list):
    try:
        for entry in directory.iterdir():
            if entry.is_file():
                futures.append(executor.submit(copy_file, entry, target_root))
            elif entry.is_dir():
                process_directory(entry, target_root, executor, futures)
    except Exception as e:
        print(f"Помилка при обробці {directory}: {e}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Сортування файлів за розширенням.")
    parser.add_argument("source", help="Шлях до директорії з файлами.")
    parser.add_argument("destination", nargs="?", default="dist", help="Цільова директорія (за замовчуванням dist).")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    target_path = Path(args.destination).resolve()

    if not source_path.exists() or not source_path.is_dir():
        print(f"Джерельна директорія '{source_path}' не знайдена.")
        sys.exit(1)

    target_path.mkdir(parents=True, exist_ok=True)

    futures = []

    with ThreadPoolExecutor() as executor:
        process_directory(source_path, target_path, executor, futures)
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Помилка: {e}")

    print("Готово. Файли скопійовано за розширеннями.")

if __name__ == "__main__":
    main()
