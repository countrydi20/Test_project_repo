import os
from google.cloud import storage
from google.api_core import retry

def download_bucket(bucket_name: str, destination_dir: str, prefix: str = "") -> None:
    print(os.getcwd())

    os.makedirs(destination_dir, exist_ok=True) # What does this do, Diana?

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Diana, blobs are basically chunks of files to be downloaded. This is important because you don't want to put
    # all the images in the RAM (your PC will get super slow if you do).
    blobs = client.list_blobs(bucket_name, prefix=prefix)

    # Why are we using this line?
    gcs_retry = retry.Retry(
        predicate=retry.if_transient_error,
        deadline=300.0,
    )

    count = 0 # Why do we need this object? (tip: check below)
    skipped = 0 # Why do we need this object? (tip: check below)

    for blob in blobs:
        # Skip "directory placeholders" (sometimes objects end with '/') this is just for safety, but do we need it? Why, why not?
        if blob.name.endswith("/"):
            skipped += 1
            continue

        rel_path = blob.name[len(prefix):].lstrip("/") if prefix else blob.name
        local_path = os.path.join(destination_dir, rel_path)

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Skip if already downloaded with same size (quick check) # Why this?
        if os.path.exists(local_path) and os.path.getsize(local_path) == (blob.size or 0):
            skipped += 1
            continue
        #I can put an edit here?
        blob.download_to_filename(local_path, retry=gcs_retry)
        count += 1
        if count % 100 == 0:
            print(f"Downloaded {count} objects...")

    print(f"Done. Downloaded: {count}, skipped: {skipped}")

if __name__ == "__main__": # Diana, this is your homework: Next time we meet, you're explaining this weird line to me.
    download_bucket(bucket_name="hoffen1", destination_dir=os.getcwd()+r"\prototype_images")
