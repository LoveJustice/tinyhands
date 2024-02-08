import os


def list_files(directory, extension=".pdf"):
    """List files in a directory with a specific extension."""
    return sorted([file for file in os.listdir(directory) if file.endswith(extension)])


def list_dirs(directory):
    """List subdirectories in a directory, excluding '.DS_Store'."""
    return sorted(
        [
            dir
            for dir in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, dir)) and dir != ".DS_Store"
        ]
    )
