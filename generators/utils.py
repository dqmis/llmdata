import json
import os


def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def export_problems(
    problems: list[dict],
    data_dir: str,
):

    asp_dir = os.path.join(data_dir, "asp_code")
    images_dir = os.path.join(data_dir, "images")

    create_directory(data_dir)
    create_directory(asp_dir)
    create_directory(images_dir)

    for i, problem in enumerate(problems):
        id = f"problem_{i}"
        asp_path = os.path.join(asp_dir, f"{id}.asp")
        image_path = os.path.join(images_dir, f"{id}.png")

        problem["image"].savefig(image_path)
        with open(asp_path, "w") as f:
            f.write(problem["asp"])

        del problems[i]["asp"]
        del problems[i]["image"]
        problems[i]["id"] = id

    # Save the problems to a json file
    with open(os.path.join(data_dir, "data.json"), "w") as f:
        json.dump(problems, f, indent=4)
