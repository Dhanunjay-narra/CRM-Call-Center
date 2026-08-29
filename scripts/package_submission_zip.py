import os
import zipfile
import shutil

BASE_DIR = r"c:\Users\DHANUNJAY\OneDrive\Desktop\git project folders\git8"
DEST_ZIP_1 = r"c:\Users\DHANUNJAY\OneDrive\Desktop\git project folders\git8\CallSphere-CRM.zip"
DEST_ZIP_2 = r"c:\Users\DHANUNJAY\OneDrive\Desktop\git project folders\CallSphere-CRM.zip"

EXCLUDE_DIRS = {
    'venv', '.venv', '__pycache__', '.pytest_cache', 'node_modules', '.next',
    'coverage', 'dist', 'build', 'htmlcov',
    'git1', 'git2', 'git3', 'git4', 'git5', 'git6', 'git7'
}

EXCLUDE_FILES = {
    'CallSphere-CRM.zip'
}

def create_zip():
    print(f"Creating submission zip at {DEST_ZIP_1}...")
    if os.path.exists(DEST_ZIP_1):
        os.remove(DEST_ZIP_1)

    file_count = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(DEST_ZIP_1, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Exclude unwanted directories but KEEP .git
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES or file.endswith('.pyc'):
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_DIR)
                
                zipf.write(full_path, rel_path)
                file_count += 1
                total_uncompressed_bytes += os.path.getsize(full_path)

    print(f"Successfully packaged {file_count} files ({total_uncompressed_bytes / (1024*1024):.2f} MB uncompressed).")
    print(f"Zip archive size: {os.path.getsize(DEST_ZIP_1) / (1024*1024):.2f} MB")
    
    # Copy to parent folder as well
    shutil.copy2(DEST_ZIP_1, DEST_ZIP_2)
    print(f"Copied zip to {DEST_ZIP_2}")

if __name__ == "__main__":
    create_zip()
