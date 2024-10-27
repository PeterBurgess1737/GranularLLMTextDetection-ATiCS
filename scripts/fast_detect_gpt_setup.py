import pathlib
import shutil


def main():
    # Find the location of the necessary script
    my_location = pathlib.Path(__file__).parent
    script_location = my_location / "fast_detect_gpt_client.py"

    # Find the new location in the Fast DetectGPT repo
    new_location = my_location.parent / "fast-detect-gpt" / "scripts" / "fast_detect_gpt_client.py"
    if not new_location.parent.exists():
        raise ValueError(f"Directory {new_location.parent} does not exist")

    # Move it into the Fast DetectGPT repo
    shutil.copy(script_location, new_location)


if __name__ == "__main__":
    main()
