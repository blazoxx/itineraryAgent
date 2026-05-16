import json
import os


def save_cache(
    filename,
    data
):

    os.makedirs(
        "cache",
        exist_ok=True
    )

    with open(
        f"cache/{filename}.json",
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


def load_cache(
    filename
):

    path = f"cache/{filename}.json"

    if os.path.exists(path):

        with open(path, "r") as f:
            return json.load(f)

    return None