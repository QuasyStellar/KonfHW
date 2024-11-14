import zipfile

with zipfile.ZipFile("vfs.zip", "w") as zipf:
    zipf.writestr("dir1/file1.txt", "This is file 1")
    zipf.writestr("dir1/file2.txt", "This is file 2")
    zipf.writestr("dir2/file3.txt", "This is file 3")
    zipf.writestr("file4.txt", "This is file 4")

import json

config = {"username": "user1", "vfs_path": "vfs.zip", "startup_script": "startup.sh"}

with open("config.json", "w") as f:
    json.dump(config, f, indent=4)
