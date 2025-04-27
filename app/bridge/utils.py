def remove_file_url_prefix(file_url: str) -> str:
        prefix = 'file://'
        if file_url.startswith(prefix):
            file_url = file_url.removeprefix(prefix)

        return file_url
