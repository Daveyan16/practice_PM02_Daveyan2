import hashlib

filename = "backup.tar.gz"

with open(filename, "rb") as f:
    sha256 = hashlib.sha256(
        f.read()
    ).hexdigest()

print("SHA256:", sha256)