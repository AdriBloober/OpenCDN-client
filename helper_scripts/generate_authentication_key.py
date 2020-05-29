import base64
from sys import argv

from Crypto.PublicKey import RSA

MAXIMAL_LENGTH_OF_RSA_KEY = 2048


def cli_help():
    print("Help:")
    print(f"{__file__} <length of rsa key> <output_file_for_private_key>")
    exit(1)


if __name__ == "__main__":
    args = argv[1:]
    if len(args) != 2:
        cli_help()
    length_of_rsa_key = int(args[0])
    output_file_for_private_key = args[1]
    if length_of_rsa_key == 0 or length_of_rsa_key > MAXIMAL_LENGTH_OF_RSA_KEY:
        raise ValueError(f"The rsa key length should be higher than 0 and lower than {MAXIMAL_LENGTH_OF_RSA_KEY}.")
    key = RSA.generate(length_of_rsa_key)
    exported_public_key = key.publickey().export_key("DER")
    exported_private_key = key.export_key("DER")
    print("Public Key: ")
    print(base64.b64encode(exported_public_key).decode("utf-8"))
    with open(output_file_for_private_key, 'wb') as file:
        file.write(exported_private_key)
