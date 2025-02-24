import boto3
import zipfile
import os
from datetime import datetime
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import time

load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)
bucket_name = os.getenv('S3_BUCKET_NAME')

DATA_DIR = "data"
ALLOWED_EXTENSIONS = ('.jpg', '.txt', '.wav')


def upload_to_s3():
    """壓縮 data 資料夾中的 .jpg、.txt、.wav 檔案並上傳至 S3，上傳成功後刪除這些檔案"""
    if not os.path.exists(DATA_DIR):
        print("Data directory does not exist, nothing to upload.")
        return

    files_to_upload = [
        os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR)
        if f.lower().endswith(ALLOWED_EXTENSIONS) and os.path.isfile(os.path.join(DATA_DIR, f))
    ]

    if not files_to_upload:
        print("No .jpg, .txt, or .wav files found in data directory to upload.")
        return

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    zip_file = os.path.join(DATA_DIR, f"{timestamp}.zip")

    try:
        print(f"Compressing files into '{zip_file}'...")
        with zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in files_to_upload:
                zf.write(file_path, os.path.basename(file_path))
                print(f"Added '{file_path}' to ZIP")

        print(f"Uploading '{zip_file}' to S3...")
        for attempt in range(3):
            try:
                s3_client.upload_file(zip_file, bucket_name, os.path.basename(zip_file))
                print(f"Successfully uploaded '{zip_file}' to S3")
                break
            except ClientError as e:
                print(f"Upload failed (attempt {attempt + 1}): {e}")
                time.sleep(2)
                if attempt == 2:
                    raise Exception("Upload failed after 3 attempts, please check network")

        if os.path.exists(zip_file):
            os.remove(zip_file)
            print(f"Deleted ZIP file '{zip_file}'")

        for file_path in files_to_upload:
            if os.path.exists(file_path) and file_path.lower().endswith(ALLOWED_EXTENSIONS):
                os.remove(file_path)
                print(f"Deleted original file '{file_path}'")
            else:
                print(f"File '{file_path}' not found or not a .jpg/.txt/.wav file, skipping deletion")

    except Exception as e:
        print(f"Upload process failed: {e}")


if __name__ == "__main__":
    upload_to_s3()
