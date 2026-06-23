import subprocess
import hashlib
import boto3
from datetime import datetime

def backup_node(node_path, bucket):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    archive = f"snapshot_{timestamp}.tar.gz"

    subprocess.run(
        f"tar -czf {archive} {node_path}",
        shell=True,
        check=True
    )

    with open(archive, "rb") as f:
        checksum = hashlib.sha256(
            f.read()
        ).hexdigest()

    s3 = boto3.client("s3")

    s3.upload_file(
        archive,
        bucket,
        archive
    )

    print(checksum)

backup_node("/bitcoin", "coinguard-backups")