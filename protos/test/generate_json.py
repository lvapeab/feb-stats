import json
import glob
import os
from base64 import encodebytes

if __name__ == "__main__":
    boxscores_dir = "test_data"
    boxscores_list = []
    for (i, link) in enumerate(
        glob.iglob(os.path.join(str(boxscores_dir), "*.html"), recursive=False)
    ):
        with open(link, mode="rb") as f:
            boxscore_bytes = f.read()
        boxscores_list.append(encodebytes(boxscore_bytes).decode("latin1"))

    with open("protos/minidata.json", mode="w") as f:
        json.dump({"boxscores": boxscores_list}, f, ensure_ascii=False)
    print(f"Written {len(boxscores_list)} records")
