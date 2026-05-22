import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

def generate_key_from_password(password: str, salt: bytes = None) -> bytes:
    """
    Generate a Fernet key from a password using PBKDF2.
    
    Args:
        password (str): The user's password
        salt (bytes): Salt for key derivation (optional, generates new if None)
    
    Returns:
        bytes: The derived key for encryption/decryption
    """
    if salt is None:
        salt = b'secure_media_salt_2024'  # Fixed salt for consistency
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(file_content: bytes, key: bytes) -> bytes:
    """
    Encrypt file content using Fernet symmetric encryption.
    
    Args:
        file_content (bytes): The content to encrypt
        key (bytes): The encryption key
    
    Returns:
        bytes: Encrypted content
    """
    try:
        fernet = Fernet(key)
        encrypted_content = fernet.encrypt(file_content)
        return encrypted_content
    except Exception as e:
        raise Exception(f"Encryption failed: {str(e)}")

def decrypt_file(encrypted_content: bytes, key: bytes) -> bytes:
    """
    Decrypt file content using Fernet symmetric encryption.
    
    Args:
        encrypted_content (bytes): The encrypted content
        key (bytes): The decryption key
    
    Returns:
        bytes: Decrypted content
    """
    try:
        fernet = Fernet(key)
        decrypted_content = fernet.decrypt(encrypted_content)
        return decrypted_content
    except Exception as e:
        raise Exception(f"Decryption failed: Invalid key or corrupted file")

def generate_file_hash(content: bytes) -> str:
    """
    Generate SHA256 hash of file content for integrity verification.
    
    Args:
        content (bytes): File content
    
    Returns:
        str: Hexadecimal hash string
    """
    return hashlib.sha256(content).hexdigest()

def obfuscate_filename(original_name: str) -> str:
    """
    Generate an obfuscated filename that doesn't reveal the original.
    
    Args:
        original_name (str): Original filename
    
    Returns:
        str: Obfuscated filename
    """
    # Create hash of original name with timestamp for uniqueness
    timestamp = str(hash(original_name + str(os.urandom(8))))
    hash_object = hashlib.md5(timestamp.encode())
    obfuscated = hash_object.hexdigest()
    
    # Use a non-obvious extension
    return f"{obfuscated}.tmp"
