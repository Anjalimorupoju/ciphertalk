import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from django.conf import settings


class AESCipher:
    """
    AES-256-CBC encryption for message content
    """
    def __init__(self, key=None):
        self.key = key or get_random_bytes(32)  # 256-bit key

    def encrypt(self, plaintext):
        """Encrypt plaintext using AES-256-CBC"""
        try:
            iv = get_random_bytes(16)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            encrypted = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
            return base64.b64encode(iv + encrypted).decode('utf-8')
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")

    def decrypt(self, encrypted_data):
        """Decrypt AES-256-CBC encrypted data"""
        try:
            raw = base64.b64decode(encrypted_data)
            iv = raw[:16]
            encrypted = raw[16:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

    def get_key_b64(self):
        """Get base64 encoded key for storage"""
        return base64.b64encode(self.key).decode('utf-8')

    @classmethod
    def from_b64_key(cls, b64_key):
        """Create cipher from base64 encoded key"""
        key = base64.b64decode(b64_key)
        return cls(key)


class RSACipher:
    """
    RSA encryption for secure key exchange
    """
    def __init__(self):
        self.key_size = 2048

    def generate_key_pair(self):
        """Generate RSA public/private key pair"""
        key = RSA.generate(self.key_size)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    def encrypt_with_public_key(self, public_key_pem, data):
        """Encrypt data using RSA public key"""
        try:
            public_key = RSA.import_key(public_key_pem)
            cipher = PKCS1_OAEP.new(public_key)
            encrypted = cipher.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            raise Exception(f"RSA encryption failed: {str(e)}")

    def decrypt_with_private_key(self, private_key_pem, encrypted_data):
        """Decrypt data using RSA private key"""
        try:
            private_key = RSA.import_key(private_key_pem)
            cipher = PKCS1_OAEP.new(private_key)
            encrypted_bytes = base64.b64decode(encrypted_data)
            decrypted = cipher.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise Exception(f"RSA decryption failed: {str(e)}")


class ChatEncryptionManager:
    """
    High-level encryption manager for chat messages
    """
    def __init__(self):
        self.aes_cipher = AESCipher()
        self.rsa_cipher = RSACipher()

    def generate_user_keys(self):
        """Generate RSA key pair for a user"""
        private_key, public_key = self.rsa_cipher.generate_key_pair()
        return {
            'private_key': private_key.decode('utf-8'),
            'public_key': public_key.decode('utf-8')
        }

    def encrypt_message(self, plaintext, recipient_public_key=None):
        """
        Encrypt a message for storage and transmission
        Returns: {
            'encrypted_content': AES-encrypted message,
            'encrypted_key': RSA-encrypted AES key (if recipient provided),
            'iv': initialization vector
        }
        """
        # Encrypt message with AES
        encrypted_content = self.aes_cipher.encrypt(plaintext)
        
        result = {
            'encrypted_content': encrypted_content,
            'aes_key': self.aes_cipher.get_key_b64()
        }
        
        # If recipient public key provided, encrypt the AES key
        if recipient_public_key:
            encrypted_key = self.rsa_cipher.encrypt_with_public_key(
                recipient_public_key.encode('utf-8'),
                result['aes_key']
            )
            result['encrypted_key'] = encrypted_key
        
        return result

    def decrypt_message(self, encrypted_content, aes_key_b64=None, private_key=None, encrypted_key=None):
        """
        Decrypt a message using either direct AES key or RSA-encrypted key
        """
        if aes_key_b64:
            # Direct AES key provided
            cipher = AESCipher.from_b64_key(aes_key_b64)
            return cipher.decrypt(encrypted_content)
        elif private_key and encrypted_key:
            # RSA-encrypted key provided
            aes_key = self.rsa_cipher.decrypt_with_private_key(
                private_key.encode('utf-8'),
                encrypted_key
            )
            cipher = AESCipher.from_b64_key(aes_key)
            return cipher.decrypt(encrypted_content)
        else:
            raise Exception("Insufficient parameters for decryption")


# Global instance
encryption_manager = ChatEncryptionManager()