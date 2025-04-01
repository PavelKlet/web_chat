from pathlib import Path
import os


from fastapi import UploadFile
from urllib.parse import urlparse
from aiofiles import open


async def save_and_get_avatar_path(avatar: UploadFile, user_id: int) -> str:
    filename = os.path.basename(urlparse(avatar.filename).path)
    filename_without_extension = Path(filename).stem
    file_extension = Path(filename).suffix
    user_directory = f"media/{user_id}"

    os.makedirs(user_directory, exist_ok=True)
    file_list = os.listdir(user_directory)

    if file_list:
        for file_name in file_list:
            file_path = os.path.join(user_directory, file_name)
            os.remove(file_path)

    new_filename = f"{filename_without_extension}{file_extension}"
    upload_path = f"{user_directory}/{new_filename}"

    async with open(upload_path, "wb") as file:
        content = await avatar.read()
        await file.write(content)

    return "/" + upload_path
