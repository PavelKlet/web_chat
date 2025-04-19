from pathlib import Path
import os

from fastapi import UploadFile
from urllib.parse import urlparse
from aiofiles import open

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MEDIA_DIR = BASE_DIR / "media"

async def save_and_get_avatar_path(avatar: UploadFile, user_id: int) -> str:
    filename = os.path.basename(urlparse(avatar.filename).path)
    filename_without_extension = Path(filename).stem
    file_extension = Path(filename).suffix

    user_directory = MEDIA_DIR / str(user_id)
    user_directory.mkdir(parents=True, exist_ok=True)


    for file in user_directory.iterdir():
        file.unlink()

    new_filename = f"{filename_without_extension}{file_extension}"
    upload_path = user_directory / new_filename

    async with open(upload_path, "wb") as file:
        content = await avatar.read()
        await file.write(content)

    return f"/media/{user_id}/{new_filename}"
