import os

class StorageService:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def get_file_path(self, filename: str) -> str:
        return os.path.join(self.upload_dir, filename)

    # Future methods for saving, deleting files etc.
storage_service = StorageService()
