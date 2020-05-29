"""
open_cdn.client
~~~~~~~~~~~~

This module implements the authentication.
:copyright: (c) 2020 by AdriBloober.
:license: GNU General Public License v3.0
"""

import base64

import requests
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from open_cdn.errors import parse_error, BasicError


class AuthenticationManager:
    """The AuthenticationManger manages all authentication tokens.
    :param client: The client is required to use the :class:`FileManager`.
    """

    def __init__(self, client):
        self.client = client

    def create_authentication_token(self, key_identifier, private_key: RSA.RsaKey):
        """Create new authentication token
        :param key_identifier: The identifier of the key (the variable key on the server).
        :param private_key: The :class:`RSA.RsaKey` Key for authentication.
        :return: string authentication_token
        """
        response = requests.post(
            f"{self.client.api_url}/authentication",
            data={"key_identifier": key_identifier},
        )
        j = parse_error(response)
        encrypted_authentication_token = j["encrypted_authentication_token"]
        return (
            PKCS1_OAEP.new(private_key)
            .decrypt(base64.b64decode(encrypted_authentication_token.encode("utf-8")))
            .decode("utf-8")
        )

    def test_authentication(self, authentication_token):
        """Test the authentication token (Attention: don't use this function in production, because the action needs some time).
        :param authentication_token: The authentication token to authenticate.
        :return:
        """
        response = requests.post(
            f"{self.client.api_url}/authentication/test",
            data={"authentication_token": authentication_token},
        )
        j = parse_error(response)
        if not ("status" in j and j["status"] == "success"):
            raise BasicError()

    def delete_authentication_token(self, authentication_token):
        """Delete a authentication token on the server.
        :param authentication_token: The authentication token to authenticate.
        :return:
        """
        response = requests.delete(
            f"{self.client.api_url}/authentication",
            data={"authentication_token": authentication_token},
        )
        j = parse_error(response)
        if not ("status" in j and j["status"] == "success"):
            raise BasicError()
