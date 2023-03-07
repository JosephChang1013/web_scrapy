from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel

from google.cloud import storage


class BaseResponse(BaseModel):
    success: bool
    error_msg: str
    dict_data: Optional[dict]
    result: Optional[tuple]
    json_data: Optional[list]
    keyword_list: Optional[list]


class BqAccountRawText(BaseModel):
    account_id: Optional[str] = None
    raw_text: Optional[str] = None
    raw_text_zh_en: Optional[str] = None


class DomainName(str, Enum):
    ETTODAY = 'ettoday'
    NOWNEWS = 'nownews'
    UDNNEWS = 'udn'
    CHINATIME = 'chinatimes'
    TVBSNEWS = 'tvbs'
    DCARD = 'dcard'
    PTT = 'ptt'
    FACEBOOK = 'facebook'


def set_blob_metadata(bucket_name, blob):
    """Set a blob's metadata."""
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    # blob = bucket.get_blob(blob_name)
    metadata = {'updated': f"{datetime.now().replace(tzinfo=None)}"}
    blob.metadata = metadata
    blob.patch()
    return metadata.update()


def blob_metadata(bucket_name, blob):
    """Prints out a blob's metadata."""
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Retrieve a blob, and its metadata, from Google Cloud Storage.
    # Note that `get_blob` differs from `Bucket.blob`, which does not
    # make an HTTP request.
    blob = bucket.get_blob(blob.name)

    print(f"Blob: {blob.name}")
    print(f"Bucket: {blob.bucket.name}")
    print(f"Storage class: {blob.storage_class}")
    print(f"ID: {blob.id}")
    # print(f"Size: {blob.size} bytes")
    print(f"Updated: {blob.updated}")
    # print(f"Generation: {blob.generation}")
    # print(f"Metageneration: {blob.metageneration}")
    # print(f"Etag: {blob.etag}")
    # print(f"Owner: {blob.owner}")
    # print(f"Component count: {blob.component_count}")
    # print(f"Crc32c: {blob.crc32c}")
    # print(f"md5_hash: {blob.md5_hash}")
    # print(f"Cache-control: {blob.cache_control}")
    print(f"Content-type: {blob.content_type}")
    # print(f"Content-disposition: {blob.content_disposition}")
    # print(f"Content-encoding: {blob.content_encoding}")
    # print(f"Content-language: {blob.content_language}")
    print(f"Metadata: {blob.metadata}")
    # print(f"Medialink: {blob.media_link}")
    # print(f"Custom Time: {blob.custom_time}")
    print("Temporary hold: ", "enabled" if blob.temporary_hold else "disabled")
    print(
        "Event based hold: ",
        "enabled" if blob.event_based_hold else "disabled",
    )
    if blob.retention_expiration_time:
        print(
            f"retentionExpirationTime: {blob.retention_expiration_time}"
        )
    return blob.updated.replace(tzinfo=None)
