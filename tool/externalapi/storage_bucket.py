from google.cloud import storage

storage_client = storage.Client()

bucket_name = 'web_scrapper_v1'
bucket = storage_client.bucket(bucket_name)

"""

Upload Files

"""


def upload_file_to_bucket(contents, destination_blob_name):
    """Uploads a file to the bucket."""

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The contents to upload to the file
    # contents = "these are my contents"

    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents)
    return blob


"""

Dowload Files

"""


def download_blob_into_memory(destination_blob_name) -> bytes:
    """Downloads a blob into memory."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # blob_name = "storage-object-name"

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(destination_blob_name)
    contents = blob.download_as_string()
    return contents
