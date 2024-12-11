import glob
import json
import logging
import os
from base64 import encodebytes

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    boxscores_dir = "data"
    boxscores_list = []
    for i, link in enumerate(glob.iglob(os.path.join(str(boxscores_dir), "*.html"), recursive=False)):
        with open(link, mode="rb") as f:
            boxscore_bytes = f.read()
        boxscores_list.append(encodebytes(boxscore_bytes).decode("latin1"))

    with open("protos/minidata.json", mode="w") as f:  # type:ignore
        json.dump({"boxscores": boxscores_list}, f, ensure_ascii=False)  # type:ignore
    logger.info(f"Written {len(boxscores_list)} records")
