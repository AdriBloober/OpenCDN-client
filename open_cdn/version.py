"""
open_cdn.client
~~~~~~~~~~~~

This module implements the version management.
:copyright: (c) 2020 by AdriBloober.
:license: GNU General Public License v3.0
"""
import requests

from open_cdn.errors import parse_error

CLIENT_VERSION = 10


class VersionDiscrepancy(Exception):
    """If the client have a older or newer version than the server, this error would thrown."""
    pass


class VersionManager:
    """The VersionManager would manage the version management.
    :param client: The client is required to use the :class:`FileManager`.
    """
    def __init__(self, client):
        self.client = client

    def check_version(self):
        """Check the version of the client and the server.
        :return:
        """
        response = requests.get(self.client.api_url)
        parse_error(response, json=False)
        version = int(response.content.decode("utf-8").split("\n")[1])
        if version != CLIENT_VERSION:
            raise VersionDiscrepancy(
                f"The Version of the server is {version} and the version of the client {CLIENT_VERSION}: Please "
                f"update the client or the server! "
            )
