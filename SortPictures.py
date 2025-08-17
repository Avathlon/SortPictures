#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SortPictures
- Sort pictureas and videos to folders by month and year.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# ---- Konfiguraatio ---- #
SRC_DIR   = "E:\Kuvat\Lajittele"      # Source directory root folder (pics + videos)
DEST_ROOT = "E:\Kuvat\Lajiteltu"           # Sorted pics and videos root folder

# ----------------------- #

def get_exif_date(path: Path) -> datetime | None:
    """Lataa EXIF‑päivämäärän, jos se on saatavilla."""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        img = Image.open(path)
        exif_data = img._getexif()
        if not exif_data:
            return None

        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == "DateTimeOriginal":
                try:
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    return None
    except Exception:
        pass

    return None


def get_file_mtime(path: Path) -> datetime:
    """Palauttaa tiedoston muokkausajan (timestamp)."""
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts)


def organize_photos_and_videos():
    src_dir   = Path(SRC_DIR).expanduser().resolve()
    dest_root = Path(DEST_ROOT).expanduser().resolve()

    if not src_dir.is_dir():
        raise FileNotFoundError(f"Lähdehakemistoa {src_dir} ei löydy")

    photo_exts = {".jpg", ".jpeg", ".png", ".raw", ".pef"}
    video_exts = {".mp4"}

    for file_path in src_dir.rglob("*"):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()

        # ---------- VIDEO ----------
        if ext in video_exts:
            date_obj = get_file_mtime(file_path)   # fallback: mtime
            year, month = f"{date_obj.year:04d}", f"{date_obj.month:02d}"
            dest_dir = dest_root / "videos" / year / month

        # ---------- PHOTO ----------
        elif ext in photo_exts:
            date_obj = get_exif_date(file_path) or get_file_mtime(file_path)
            year, month = (
                f"{date_obj.year:04d}",
                f"{date_obj.month:02d}",
            )
            dest_dir = dest_root / "photos" / year / month

        else:
            # Ei halutun tiedostopäätteen
            continue

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / file_path.name

        print(f"Siirretään: {file_path} → {dest_path}")

        try:
            shutil.move(str(file_path), str(dest_path))
        except Exception as e:
            print(f"[ERROR] Siirtäessä {file_path}: {e}")


if __name__ == "__main__":
    organize_photos_and_videos()