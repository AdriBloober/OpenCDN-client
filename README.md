# OpenCDN-client (Python official client)

A client to communicate with the OpenCDN backend.

## Installation

Verify that you have installed python3.8 and pip3!  
``python3.8 -m pip install -r requirements.txt`` to install the dependencies.

## Helper Scripts
### generate_authentication_key
If you use on the server a authentication key/token, you can generate the key with this script. The first argument is
the keysize (maximum 2048) and the second argument is the filepath to the output privatekey file.