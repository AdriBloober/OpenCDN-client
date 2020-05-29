"""
open_cdn.client
~~~~~~~~~~~~

This module implements the error management. To watch the description of the errors, look at the server.
:copyright: (c) 2020 by AdriBloober.
:license: GNU General Public License v3.0
"""

import requests


class BasicError(Exception):
    id = 0
    name = "basic_error"
    http_return = 500

    def to_json(self):
        return {"id": self.id, "name": self.name}


class NoFileInRequest(BasicError):
    id = 1
    name = "no_file_in_request"
    http_return = 400


class InvalidFileSuffix(BasicError):
    id = 2
    name = "invalid_file_suffix"
    http_return = 403


class InvalidFileName(BasicError):
    id = 3
    name = "invalid_file_name"
    http_return = 403


class BadRequest(BasicError):
    id = 4
    name = "bad_request"
    http_return = 400


class FileDoesNotExists(BasicError):
    id = 5
    name = "file_does_not_exists"
    http_return = 404


class FileTooBig(BasicError):
    id = 6
    name = "file_too_big"
    http_return = 403


class AccessDenied(BasicError):
    id = 7
    name = "access_denied"
    http_return = 403


class ActionNeedsAuthenticationToken(BasicError):
    id = 8
    name = "action_needs_authentication_token"
    http_return = 400


class AuthenticationKeyNotFound(BasicError):
    id = 9
    name = "authentication_key_not_found"
    http_return = 404


class InvalidAuthenticationToken(BasicError):
    id = 10
    name = "invalid_authentication_token"
    http_return = 403


available_errors = {
    BasicError,
    NoFileInRequest,
    InvalidFileSuffix,
    InvalidFileName,
    BadRequest,
    FileDoesNotExists,
    FileTooBig,
    AccessDenied,
    ActionNeedsAuthenticationToken,
    AuthenticationKeyNotFound,
    InvalidAuthenticationToken,
}


def parse_error(response: requests.Response, check_json=False, json=True):
    """Test if any error thrown.
    :param response: The requests :class:`requests.Response`
    :param check_json: Check if the response is json.
    :param json: Enable JSON Error checking.
    :return: dict the json of the response (response.json()).
    """
    if check_json and not response.content.startswith(b"{"):
        response.raise_for_status()
        return None
    if json:
        j = response.json()
        if "status" in j and j["status"] == "error":
            for available_error in available_errors:
                if available_error.id == int(j["id"]) and available_error.name == j["name"]:
                    raise available_error()
            raise BasicError()
        response.raise_for_status()
        return j
    response.raise_for_status()
