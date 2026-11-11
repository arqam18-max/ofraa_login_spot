"""写真のチェックと保存"""
import os
import uuid

ALLOWED_EXT = {"jpg", "jpeg", "png"}
MAX_FILES = 3
MAX_SIZE = 5 * 1024 * 1024  # 5MB


def validate_photo(storage):
    """問題があればエラーメッセージ、なければ None"""
    name = storage.filename or ""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ALLOWED_EXT:
        return f"写真は jpg / png のみ登録できます（{name}）"
    head = storage.stream.read(8)
    storage.stream.seek(0)
    ok = head.startswith(b"\xff\xd8\xff") if ext in ("jpg", "jpeg") else head.startswith(b"\x89PNG\r\n\x1a\n")
    if not ok:
        return f"写真のファイル形式が正しくありません（{name}）"
    storage.stream.seek(0, os.SEEK_END)
    size = storage.stream.tell()
    storage.stream.seek(0)
    if size > MAX_SIZE:
        return f"写真は1枚5MB以内にしてください（{name}）"
    return None


def save_photo(storage, upload_folder):
    """保存して static からの相対パスを返す"""
    ext = storage.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    storage.save(os.path.join(upload_folder, filename))
    return f"uploads/{filename}"
