import os

def remove_file_url_prefix(file_url: str) -> str:
        prefix = 'file://'
        if file_url.startswith(prefix):
            file_url = file_url.removeprefix(prefix)

        return file_url

def get_log_file_path():
    project_root = os.path.dirname(os.path.dirname(__file__))  # opentas/
    log_path = os.path.join(project_root, "log.txt")
    return log_path