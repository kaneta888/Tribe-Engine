import os
from werkzeug.utils import secure_filename
from flask import current_app, url_for

class LocalStorage:
    def save(self, file_storage, filename):
        """Save file to local static/uploads directory."""
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file_storage.save(filepath)
        
        # Return the URL for the file
        return url_for('static', filename=f'uploads/{filename}')

class S3Storage:
    def __init__(self):
        import boto3
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'ap-northeast-1')
        )
        self.bucket_name = os.environ.get('S3_BUCKET_NAME')

    def save(self, file_storage, filename):
        """Upload file to AWS S3 bucket."""
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME is not set")

        try:
            self.s3.upload_fileobj(
                file_storage,
                self.bucket_name,
                filename,
                ExtraArgs={
                    "ContentType": file_storage.content_type,
                    # "ACL": "public-read" # Uncomment if bucket is public, or using CloudFront
                }
            )
            # Assuming standard S3 URL structure (or CloudFront)
            region = os.environ.get('AWS_REGION', 'ap-northeast-1')
            return f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{filename}"
        except Exception as e:
            current_app.logger.error(f"S3 Upload Error: {e}")
            raise e

def get_storage_provider():
    """Return S3Storage if configured, otherwise LocalStorage."""
    if os.environ.get('USE_S3', 'False').lower() == 'true':
        return S3Storage()
    return LocalStorage()
