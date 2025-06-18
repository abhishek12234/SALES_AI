import asyncio
from appwrite.client import Client
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role
from typing import Union, Tuple, Any
from starlette.datastructures import UploadFile
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Appwrite Config
APPWRITE_ENDPOINT = 'https://fra.cloud.appwrite.io/v1'
APPWRITE_PROJECT = '6850ff0a0015b2b3c9be'
APPWRITE_API_KEY = 'standard_e61aac661b27f0eab9786405ffc8c3de29f3537932daa879ab368dc407282518a5e73aab355a565bbac8fc7235fa930c3ed712ba820d9e4adfc9649297b17bc885aca3cb2f9c7e6cfd1936aaa8c64333f2557ba6c5edd587ebd8e3d4594175b54fc15a8a4c09c85dd74a973370d3b25cfe0bf520f248bed5d62adefbdf83941d'
BUCKET_ID = '6850ff8100384d310e11'

def get_sync_client():
    client = Client()
    return client.set_endpoint(APPWRITE_ENDPOINT)\
                 .set_project(APPWRITE_PROJECT)\
                 .set_key(APPWRITE_API_KEY)

async def get_appwrite_client():
    return await asyncio.to_thread(get_sync_client)

async def add_file(file: Any) -> dict:
    """
    Uploads a file to Appwrite storage.

    Args:
        file: Either a Starlette UploadFile object or a tuple (bytes, filename)

    Returns:
        dict: Appwrite file upload response containing file metadata

    Raises:
        Exception: If file upload fails
    """
    try:
        def _upload_file(file_bytes: bytes, filename: str):
            client = get_sync_client()
            storage = Storage(client)

            # Create input file from bytes
            input_file = InputFile.from_bytes(file_bytes, filename=filename)

            # Upload file to Appwrite
            return storage.create_file(
                bucket_id=BUCKET_ID,
                file_id=ID.unique(),
                file=input_file,
                permissions=[Permission.read(Role.any())]
            )

        # Handle different input types
        if hasattr(file, 'file') and hasattr(file, 'filename'):
            logger.info(f"Processing UploadFile: {file.filename}")
            # Read file content synchronously since it's already a file object
            file_bytes = file.file.read()
            filename = file.filename
        elif isinstance(file, tuple) and len(file) == 2:
            logger.info("Processing tuple input")
            file_bytes, filename = file
            if not isinstance(file_bytes, bytes):
                raise ValueError("File content must be bytes")
        else:
            logger.error(f"Invalid file type: {type(file)}")
            raise ValueError(f"Invalid file input. Expected UploadFile or tuple(bytes, filename), got {type(file)}")

        if not file_bytes or not filename:
            raise ValueError("File content or filename is missing")

        # Upload file using thread pool
        result = await asyncio.to_thread(_upload_file, file_bytes, filename)
        logger.info(f"File uploaded successfully: {filename}")
        return result

    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        raise Exception(f"File upload failed: {str(e)}")

async def get_file_metadata(file_id: str) -> dict:
    """
    Get metadata for a file from Appwrite storage.

    Args:
        file_id: The ID of the file to get metadata for

    Returns:
        dict: File metadata

    Raises:
        Exception: If metadata retrieval fails
    """
    try:
        def _get_metadata():
            client = get_sync_client()
            storage = Storage(client)
            return storage.get_file(bucket_id=BUCKET_ID, file_id=file_id)

        return await asyncio.to_thread(_get_metadata)
    except Exception as e:
        logger.error(f"Failed to get file metadata: {str(e)}")
        raise Exception(f"Failed to get file metadata: {str(e)}")

async def get_file_url(file_id: str, mode: str = "view") -> str:
    """
    Generate a URL for accessing a file from Appwrite storage.

    Args:
        file_id: The ID of the file
        mode: Access mode ("view" or "download")

    Returns:
        str: URL for accessing the file

    Raises:
        ValueError: If mode is invalid
    """
    if mode not in ["view", "download"]:
        raise ValueError("Mode must be either 'view' or 'download'")

    return f"{APPWRITE_ENDPOINT.replace('/v1', '')}/v1/storage/buckets/{BUCKET_ID}/files/{file_id}/{mode}?project={APPWRITE_PROJECT}"