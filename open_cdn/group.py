"""
open_cdn.client
~~~~~~~~~~~~

This module implements the group management.
:copyright: (c) 2020 by AdriBloober.
:license: GNU General Public License v3.0
"""
from typing import List

import requests
from open_cdn.file import FileTarget

from open_cdn.errors import parse_error, BasicError


class GroupTarget:
    """
    In somte functions you need the group_target. If you don't have any group fetched, but you have the name,
    key and private_key you can use the group_target.
    :param name: The name of the group.
    :param key: The key of the group.
    :param private_key: The private_key of the group. The arguments are not required, but some functions need
    specify group target variables, so read the documentation of the respective function.
    """

    def __init__(self, name: str, key: str, private_key: str):
        self.name = name
        self.key = key
        self.private_key = private_key

    def __repr__(self) -> str:
        return f"open_cdn.GroupTarget name={self.name} key={self.key} private_key={self.private_key}"


class Group:
    """A OpenCDN Group with parameters and files.
    :param name: The name of the group (unique).
    :param key: The key of the group. All files which belong to this group are encrypting with this key.
    :param hashed_key: The key, but hashed.
    :param private_key: The private_key of the group. With the private_key you can delete the group,
    delete files, which belong to this group or upload new files to this group.
    :param files: A List of FileTargets, which belong to the group. You can read the list with the
    :function:`GroupManager.get`. The files are only targets, so the content of the file is not loaded.

    The key gives you read access for the group and the private_key gives you write access.
    """

    def __init__(
        self,
        name: str,
        key: str,
        hashed_key: str,
        private_key: str,
        files: List[FileTarget] = None,
    ):
        self.name = name
        self.key = key
        self.hashed_key = hashed_key
        self.private_key = private_key
        self.files = files

    def get_target(self) -> GroupTarget:
        """In some Functions you need a target to a group, so you can use this function to get the target of the group.
        :return: The target to this group.
        """
        return GroupTarget(self.name, self.key, self.private_key)

    def __repr__(self) -> str:
        return (
            f"open_cdn.Group name={self.name} key={self.key} hashed_key={self.hashed_key} "
            f"private_key={self.private_key} files={len(self.files)} "
        )


def check_group_values(group: GroupTarget, key: str, private_key=""):
    """Checks the values and replaces it with the group values.
    :param group: The group target.
    :param key:
    :param private_key: (Optional argument)
    if private_key is not set:
    :return: 'key'
    if private_key is set:
    :return: :class:`Tuple[str, str]`: (key, private_key)
    """
    if group.key is None and key is None:
        raise ValueError(
            "The GroupTarget does not provide any key, so you put the key in the function!"
        )
    if private_key != "" and group.private_key is None and private_key is None:
        raise ValueError(
            "The GroupTarget does not provide any private_key, so you put the private_key in the function!"
        )
    if key is None:
        key = group.key
    if private_key is None:
        private_key = group.private_key
    if private_key == "":
        return key
    else:
        return key, private_key


class GroupManager:
    """The GroupManager manges the groups.
    :param client:
    """

    def __init__(self, client):
        self.client = client

    def get(self, group: GroupTarget, key: str = None, private_key: str = None):
        """Fetch a group.
        :param group: The target to the group.
        :param key: The key of the group (if you have set the key in the group target, you must not set this parameter).
        :param private_key: The private_key of the group (if you have set the private_key in the group target,
                you must not set this parameter).
        :return: :class:`Group`.
        """
        key, private_key = check_group_values(group, key, private_key)
        path = f"{self.client.api_url}/group/{group.name}"
        response = requests.put(path, data={"key": key, "private_key": private_key})
        j = parse_error(response)
        return Group(
            group.name,
            key,
            j["hashed_key"],
            private_key,
            [FileTarget(key, file, group=group) for file in j["files"]],
        )

    def post(
        self, group_name: str, private_key: str = None, authentication_token: str = None
    ) -> Group:
        """Create a new group.
        :param group_name: The name of the new group.
        :param private_key: You can set a private_key. If you don't set any private_key the server will generate
                a random private_key.
        :param authentication_token: If upload_authentication is required, you must set the authentication_token.
        :return: The new :class:`Group`.
        """
        path = f"{self.client.api_url}/group/{group_name}"
        response = requests.post(
            path,
            data={
                "authentication_token": authentication_token,
                "private_key": private_key,
            },
        )
        j = parse_error(response)
        return Group(j["name"], j["key"], j["hashed_key"], j["private_key"], [])

    def delete(self, group: GroupTarget, private_key: str = None):
        """Delete a group and all files in the group.
        :param group: The target to the group.
        :param private_key: The private_key of the group (if you have set the private_key in the group target,
                you must not set this parameter).
        :return:
        """
        if group.private_key is None and private_key is None:
            raise ValueError(
                "The GroupTarget does not provide any private_key, so you put the private_key in the function!"
            )
        if private_key is None:
            private_key = group.private_key
        path = f"{self.client.api_url}/group/{group.name}"
        response = requests.delete(path, data={"private_key": private_key})
        j = parse_error(response)
        if "status" not in j or j["status"] != "success":
            raise BasicError()
