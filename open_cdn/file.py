"""
open_cdn.client
~~~~~~~~~~~~

This module implements the file management.
:copyright: (c) 2020 by AdriBloober.
:license: GNU General Public License v3.0
"""

from typing import List, Tuple

import requests

from open_cdn.group import GroupTarget, check_group_values
from open_cdn.errors import parse_error, BasicError


class FileTarget:
    """
    In some functions you need the file_target.
    If you don't have any file fetched, but you have the key and the filename you can use it in the file_target.
    :param file_or_key: If you have any file, put it in this parameter. If you would use key and filename,
    put the key here.
    :param filename: You should set it if you want to use key and filename as target.
    :param group: If the file belongs to any group, you can add this group to the target. If you would like to delete
    the file, which belongs a group, you need the group in the target.
    """

    def __init__(self, file_or_key, filename=None, group=None):
        self.group = group
        if isinstance(file_or_key, File):
            self.file = file_or_key
            self.key = file_or_key.key
            self.filename = file_or_key.filename
            self.loaded = True
        elif type(filename) == str and type(file_or_key) == str:
            self.key = file_or_key
            self.filename = filename
            self.loaded = False
        else:
            raise ValueError(
                "You should use FileTarget(file) or FileTarget(key, filename)!"
            )

    def __repr__(self) -> str:
        return f"open_cdn.FileTarget key={self.key} filename={self.filename} loaded={self.loaded} group={self.group}"


class File:
    """A OpenCDN File with the parameters
    :param key: The file is encrypted with this key. :param hashed_key: The
    hash of the key.
    :param filename: The name of the file.
    :param private_key: The key, which you can use to do some
    actions with the file: For example delete it.
    :param content: The content of the file in bytes. Attention: The
    hashed_key and private_key do only exists from default if you create it! If you create the file, the file content
    would be not loaded: You can load it yourself or use :function:`FileManager.fetch_file_content`.
    :param group: If the file belongs to any group, you can add this group to the file.
    """

    def __init__(
        self, key, hashed_key, filename, private_key, content, group: GroupTarget = None
    ):
        self.key = key
        self.hashed_key = hashed_key
        self.filename = filename
        self.private_key = private_key
        self.content = content
        self.group = group

    def get_target(self):
        """Get the file target of this file"""
        return FileTarget(self, group=self.group)

    def __repr__(self):
        return f"open_cdn.FileTarget key={self.key} hashed_key={self.hashed_key} filename={self.filename} private_key={self.private_key} group={self.group}"


class FileManager:
    """The FileManager would manage all cached_files.
    :param client: The client is required to use the :class:`FileManager`.
    """

    """If you download any file, the file manager would cache the file in this list. Files which belong to a any 
    group will not cached. """
    cached_files: List[File] = []

    def __init__(self, client):
        self.client = client

    def get(
        self,
        key,
        filename,
        group: GroupTarget = None,
        read_from_cache=True,
        write_in_cache=True,
    ):
        """Download/Get any content of the file.
        :param key: The file is encrypted with this key.
        :param filename: The name of the file.
        :param group: If you would like to download a file which belongs to any group, you must hand over the group target.
        :param read_from_cache: If the file is cached, the function would return the cached file.
        :param write_in_cache: If the file has been successfully loaded, the file would be cached.
        :return: :class:`File`
        """
        if read_from_cache and group is None:
            for file in self.cached_files:
                if file.key == key and file.filename == filename:
                    return file
        if group is None:
            response = requests.get(f"{self.client.api_url}/{key}/{filename}")
            parse_error(response, check_json=True)
            file = File(key, None, filename, None, response.content)
            if write_in_cache:
                self.cached_files.append(file)
            return file
        else:
            key = check_group_values(group, key)
            response = requests.get(
                f"{self.client.api_url}/{group.name}/{key}/{filename}"
            )
            parse_error(response, check_json=True)
            return File(key, None, filename, None, response.content, group=group)

    def post(
        self,
        raw_file,
        filename,
        group: GroupTarget = None,
        key: str = None,
        private_key: str = None,
        authentication_token=None,
    ):
        """Create/Upload a file.
        :param raw_file: The file (open it with open()).
        :param filename: The name of the file.
        :param authentication_token: If the server requires authentication for posting data,
        you should set the authentication_token.

        Group Upload
        ==========
        :param group: The target to the group of the file.
        :param key: The key of the group (
        you don't need the key, if you have hand over the key in the group target).
        :param private_key: The
        private_key of the group (you don't need the private_key, if you have hand over the private_key in the group
        target).

        :return: :class:`File`

        Usage::
            filename = 'test.test'
            file = file_manager.post(open(filename, 'r'), filename)
        """
        if group is None:
            response = requests.post(
                f"{self.client.api_url}/upload",
                files={"file": (filename, raw_file)},
                data={
                    "authentication_token": authentication_token,
                    "private_key": private_key,
                },
            )
            j = parse_error(response)
            file = File(
                j["key"], j["hashed_key"], j["filename"], j["private_key"], None
            )
        else:
            key, private_key = check_group_values(group, key, private_key)
            response = requests.post(
                f"{self.client.api_url}/upload",
                files={"file": (filename, raw_file)},
                data={
                    "authentication_token": authentication_token,
                    "group": group.name,
                    "key": key,
                    "private_key": private_key,
                },
            )
            j = parse_error(response)
            file = File(
                j["key"],
                j["hashed_key"],
                j["filename"],
                j["private_key"],
                None,
                group=group,
            )
        return file

    def delete(self, file: FileTarget, key=None, private_key=None):
        """Delete a file.
        :param file: The target of the deleting file.
        :param private_key: If the target isn't loaded, you should set a private_key yourself.

        Group File Deletion
        ==========
        If the file belongs to any group (the file.group is not None),
        the function will delete the group file automatically.
        If you don't hand over the key or private_key in the group target you need following parameters:
        :param key: The key of the group.
        :param private_key: The private_key of the group.
        """
        if (
            (not file.loaded and private_key is None)
            or (private_key is None and file.file.private_key is None)
        ) and (file.group is None or file.group.private_key is None):
            raise ValueError(
                "The file is not loaded and no private_key was set or the file doesn't have any private_key"
            )
        if private_key is None:
            private_key = file.file.private_key
        if private_key is None:
            private_key = file.group.private_key
        if file.group is None:
            response = requests.delete(
                f"{self.client.api_url}/{file.key}/{file.filename}",
                data={"private_key": private_key},
            )
        else:
            key = check_group_values(file.group, key)
            response = requests.delete(
                f"{self.client.api_url}/{file.group.name}/{key}/{file.filename}",
                data={"private_key": private_key},
            )
        j = parse_error(response)
        if not ("status" in j and j["status"] == "success"):
            raise BasicError()

        for f in self.cached_files:
            if f.key == file.key and f.filename == file.filename:
                self.cached_files.remove(f)

    def drop_cache_for_file(self, file: FileTarget) -> int:
        """If any file is cached, you can delete the file with this function.
        :param file: The target of the file
        :return: The count of deleted files (0 if no file was deleted)
        """
        drop_count = 0
        for f in self.cached_files:
            if f.key == file.key and f.filename == file.filename:
                self.cached_files.remove(f)
                drop_count += 1
        return drop_count

    def get_key_and_filename_from_link(self, link: str):
        """Get the key and the filename from any link
        :param link:
        File link
        =============
        :return: :class:`Tuple[str, str]` (key, filename)

        Group link:
        =============
        :return: :class:`Tuple[str, str, str]` (group_name, key, filename)
        """
        if not link.startswith(self.client.api_url):
            raise ValueError("The link doesn't use this OpenCDN server!")
        api_url = self.client.api_url
        if api_url.endswith("/"):
            api_url = api_url[: len(api_url) - 1]
        splitted_uri = link.split(api_url)
        uri = splitted_uri[len(splitted_uri) - 1]
        content = uri.split("/")
        if len(content) == 3:
            return content[1], content[2]
        elif len(content) == 4:
            return content[1], content[2], content[3]

    def fetch_file_content(
        self, file: FileTarget, read_from_cache=True, write_in_cache=True
    ) -> File:
        """If the content of any file wasn't loaded, you can load the content here.
        :param file: The loading file target.
        :param read_from_cache: Handing over for :function:`FileManager.get`.
        :param write_in_cache: Handing over for :function:`FileManager.get`.
        :return: :class:`File` The new file with loaded content.
        """
        key = file.key
        if key is None and file.group is not None and file.group.key is not None:
            key = file.group.key
        if any([x is None for x in (key, file.filename)]):
            raise ValueError(
                "You should set the file.key and file.filename to fetch the content."
            )
        new_file = self.get(
            file.key,
            file.filename,
            read_from_cache=read_from_cache,
            write_in_cache=write_in_cache,
        )
        return new_file

    def get_link_from_file(self, file: FileTarget) -> str:
        """Get the link of any file target.

        ATTENTION: Do not share group links, if you want to share only one file. All files in a group are encrypted with
                the same key. So if you share the key, everybody can access all files.

        :param file: The file target.
        :return: string
        """
        api_url = self.client.api_url
        if api_url.endswith("/"):
            api_url = api_url[: len(api_url) - 1]
        if file.group is None:
            return f"{api_url}/{file.key}/{file.filename}"
        else:
            key = file.key
            if key is None:
                key = file.group.key
            return f"{api_url}/{file.group.name}/{key}/{file.filename}"

    def __repr__(self):
        return f"open_cdn.FileManager cached_files={len(self.cached_files)}"
