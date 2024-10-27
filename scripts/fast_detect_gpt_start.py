import pathlib
import subprocess


def fast_detect_gpt_start(**kwargs) -> subprocess.Popen:
    my_location = pathlib.Path(__file__).parent
    fast_detect_gpt_repo = my_location.parent / "fast-detect-gpt"

    # Find the venv location
    venv_location = fast_detect_gpt_repo / ".venv-py3.8" / "Scripts" / "python.exe"
    if not venv_location.exists():
        raise ValueError(f"Virtual environment {venv_location} does not exist")

    # Find the client script location
    client_location = fast_detect_gpt_repo / "scripts" / "fast_detect_gpt_client.py"
    if not client_location.exists():
        raise ValueError(f"Client script {client_location} does not exist")

    # Grab any extra arguments from kwargs
    args_list = []
    for key, value in kwargs.items():
        args_list.append(str(key))
        args_list.append(str(value))

    # Run the client script
    process = subprocess.Popen([venv_location, client_location] + args_list, cwd=fast_detect_gpt_repo,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return process


if __name__ == "__main__":
    fast_detect_gpt_start()
