import os

BASE_DIR = os.getenv("WORKSPACE_DIR", "workspace")
os.makedirs(BASE_DIR, exist_ok=True)
def safe_path(rel_path=""):
    full = os.path.abspath(os.path.join(BASE_DIR, rel_path))
    if os.path.commonpath([BASE_DIR, full]) != BASE_DIR:
        raise Exception("Access denied")
    return full

def read_file(rel_path):
    path = safe_path(rel_path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(rel_path, content):
    path = safe_path(rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "saved"

def list_files(rel_path=""):
    path = safe_path(rel_path)
    return os.listdir(path)

def delete_file(rel_path):
    path = safe_path(rel_path)
    if os.path.isfile(path):
        os.remove(path)
        return "deleted"
    raise Exception("File not found")

def make_folder(rel_path):
    path = safe_path(rel_path)
    os.makedirs(path, exist_ok=True)
    return "folder created"

def file_info(rel_path):
    path = safe_path(rel_path)
    stat = os.stat(path)
    return {
        "name": os.path.basename(path),
        "size": stat.st_size,
        "is_dir": os.path.isdir(path)
    }