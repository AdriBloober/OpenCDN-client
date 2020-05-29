"""
open_cdn.client
~~~~~~~~~~~~

This module implements the client.
:copyright: (c) 2020 by AdriBloober.
:license: GNU General Public License v3.0
"""

from open_cdn.file import FileManager
from open_cdn.authentication import AuthenticationManager
from open_cdn.version import VersionManager


class Client:
    file_manager: FileManager = None
    authentication_manager: AuthenticationManager = None
    version_manager: VersionManager = None

    def __init__(self, api_url):
        self.api_url = api_url
        self.file_manager = FileManager(self)
        self.authentication_manager = AuthenticationManager(self)
        self.version_manager = VersionManager(self)
