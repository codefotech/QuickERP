import json
import binascii
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Random import get_random_bytes
import base64
import sys


class Encryption:

    @staticmethod
    def encode_data(data, passphrase):

        try:
            key = binascii.unhexlify(
                passphrase)  # return the binary string that is represented by any hexadecimal string
            pad = lambda s: s + chr(16 - len(s) % 16) * (16 - len(s) % 16)
            iv = Random.get_random_bytes(16)  # get initial vector for AES encryption requirement
            cipher = AES.new(key, AES.MODE_CBC, iv)  # create object for AES technique
            encrypted_64 = base64.b64encode(cipher.encrypt(pad(data).encode())).decode(
                'ascii')  # encrypt data then encode by base64 technique
            iv_64 = base64.b64encode(iv).decode('ascii')
            json_data = {}
            json_data['iv'] = iv_64
            json_data['data'] = encrypted_64
            clean = base64.b64encode(json.dumps(json_data).encode('ascii')).decode()
            return clean
        except Exception as e:
            print("Cannot encrypt datas...")
            print(e)
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print("Exception type: ", exception_type)
            print("File name: ", filename)
            print("Line number: ", line_number)

    @staticmethod
    def decode_data(data, passphrase):

        try:
            unpad = lambda s: s[:-s[-1]]
            key = binascii.unhexlify(passphrase)
            encrypted = json.loads(base64.b64decode(data).decode('ascii'))
            encrypted_data = base64.b64decode(encrypted['data'])
            iv = base64.b64decode(encrypted['iv'])
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(encrypted_data)
            clean = unpad(decrypted).decode('ascii').rstrip()
            return clean
        except Exception as e:
            print("Cannot decrypt datas...")
            print(e)

    @staticmethod
    def encode_id(id, module=None):
        encoded_id = Encryption.encode_data(str(id), 'BAF4AA0B251B0C5FBAF4AA0B251B0C5F')
        return encoded_id

    @staticmethod
    def decode_id(id, module=None):
        decode_id = Encryption.decode_data(str(id), 'BAF4AA0B251B0C5FBAF4AA0B251B0C5F')
        return decode_id

    @staticmethod
    def encode(value):
        encoded_data = Encryption.encode_data(str(value), 'BAF4AA0B251B0C5FBAF4AA0B251B0C5F')
        return encoded_data

    @staticmethod
    def decode(value):
        decoded_data = Encryption.decode_data(str(value), 'BAF4AA0B251B0C5FBAF4AA0B251B0C5F')
        return decoded_data
