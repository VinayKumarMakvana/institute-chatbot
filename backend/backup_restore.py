import os
import shutil
import sqlite3
import argparse
from datetime import datetime

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BACKEND_DIR, "edubot.db")
FAISS_DIR = os.path.join(BACKEND_DIR, "vectorstore")
UPLOADS_DIR = os.path.join(BACKEND_DIR, "uploads")
BACKUPS_DIR = os.path.join(BACKEND_DIR, "backups")

def create_backup():
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUPS_DIR, f"backup_{timestamp}")
    os.makedirs(backup_path, exist_ok=True)

    # 1. SQLite Backup
    if os.path.exists(DB_FILE):
        print(f"Backing up database to {backup_path}/edubot.db")
        # Use sqlite3 backup API for safe hot copy
        with sqlite3.connect(DB_FILE) as src:
            with sqlite3.connect(os.path.join(backup_path, "edubot.db")) as dst:
                src.backup(dst)
    
    # 2. FAISS Backup
    if os.path.exists(FAISS_DIR):
        print(f"Backing up FAISS vectorstore to {backup_path}/vectorstore")
        shutil.copytree(FAISS_DIR, os.path.join(backup_path, "vectorstore"))
        
    # 3. Uploads Backup
    if os.path.exists(UPLOADS_DIR):
        print(f"Backing up uploads to {backup_path}/uploads")
        shutil.copytree(UPLOADS_DIR, os.path.join(backup_path, "uploads"))
        
    print(f"Backup completed successfully at: {backup_path}")

def restore_backup(backup_folder_name):
    backup_path = os.path.join(BACKUPS_DIR, backup_folder_name)
    if not os.path.exists(backup_path):
        print(f"Error: Backup path {backup_path} does not exist.")
        return
        
    print(f"Restoring from {backup_path}...")
    
    # 1. Restore Database
    backup_db = os.path.join(backup_path, "edubot.db")
    if os.path.exists(backup_db):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        shutil.copy2(backup_db, DB_FILE)
        print("Database restored.")
        
    # 2. Restore FAISS
    backup_faiss = os.path.join(backup_path, "vectorstore")
    if os.path.exists(backup_faiss):
        if os.path.exists(FAISS_DIR):
            shutil.rmtree(FAISS_DIR)
        shutil.copytree(backup_faiss, FAISS_DIR)
        print("FAISS vectorstore restored.")
        
    # 3. Restore Uploads
    backup_uploads = os.path.join(backup_path, "uploads")
    if os.path.exists(backup_uploads):
        if os.path.exists(UPLOADS_DIR):
            shutil.rmtree(UPLOADS_DIR)
        shutil.copytree(backup_uploads, UPLOADS_DIR)
        print("Uploads restored.")
        
    print("Restore completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup and Restore utility for Institute AI Agent")
    parser.add_argument("action", choices=["backup", "restore"], help="Action to perform")
    parser.add_argument("--folder", help="Backup folder name (required for restore)")
    
    args = parser.parse_args()
    
    if args.action == "backup":
        create_backup()
    elif args.action == "restore":
        if not args.folder:
            print("Error: --folder argument is required for restore.")
        else:
            restore_backup(args.folder)
