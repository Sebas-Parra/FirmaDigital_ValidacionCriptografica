from supabase import create_client
import os

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SERVICE_ROLE_KEY')
BUCKET = 'documentos'

_client = None

def get_client():
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
    return _client


def upload_file(storage_path: str, file_bytes: bytes, is_encrypted: bool) -> None:
    content_type = 'application/octet-stream' if is_encrypted else 'application/pdf'
    client = get_client()
    client.storage.from_(BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={'content-type': content_type, 'upsert': 'true'}
    )


def get_signed_url(storage_path: str, expires_in: int = 60) -> str:
    client = get_client()
    res = client.storage.from_(BUCKET).create_signed_url(storage_path, expires_in)
    return res['signedURL']


def delete_file(storage_path: str) -> None:
    client = get_client()
    client.storage.from_(BUCKET).remove([storage_path])
