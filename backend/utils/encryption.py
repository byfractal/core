"""
Encryption utilities for securing sensitive data.
Provides AES-256 encryption, key rotation, and secure key management.
"""

import os
import base64
import json
import time
import uuid
import hashlib
from typing import Dict, Any, Optional, Tuple, Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class EncryptionKeyManager:
    """
    Manages encryption keys with support for key rotation.
    
    Uses a master key to encrypt/decrypt data encryption keys,
    allowing for key rotation without re-encrypting all data.
    """
    
    def __init__(
        self,
        master_key: Optional[str] = None,
        keys_file_path: Optional[str] = None,
        auto_rotate_days: int = 90,
    ):
        """
        Initialize the encryption key manager.
        
        Args:
            master_key: Master key for encrypting data encryption keys
                        If not provided, will use MASTER_KEY env variable
            keys_file_path: Path to the file storing encrypted keys
                           If not provided, will use ENCRYPTION_KEYS_FILE env variable
            auto_rotate_days: Number of days after which keys should be rotated
        """
        self.master_key = master_key or os.getenv("MASTER_KEY")
        if not self.master_key:
            raise ValueError("Master key is required")
        
        # Derive a key from the master key
        self.master_key_bytes = self._derive_key(self.master_key.encode(), b"master_salt")
        self.fernet = Fernet(base64.urlsafe_b64encode(self.master_key_bytes))
        
        self.keys_file_path = keys_file_path or os.getenv("ENCRYPTION_KEYS_FILE", "encryption_keys.json")
        self.auto_rotate_days = auto_rotate_days
        self.keys = self._load_keys()
        
        # Ensure we have a current key
        if not self.keys or not self._get_current_key():
            self._generate_new_key()
    
    def _derive_key(self, password: bytes, salt: bytes, iterations: int = 100000) -> bytes:
        """
        Derive a key from a password using PBKDF2.
        
        Args:
            password: Password bytes
            salt: Salt bytes
            iterations: Number of iterations for PBKDF2
            
        Returns:
            Derived key bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password)
    
    def _load_keys(self) -> Dict[str, Dict[str, Any]]:
        """
        Load encryption keys from the keys file.
        
        Returns:
            Dictionary of key info, keyed by key ID
        """
        try:
            if os.path.exists(self.keys_file_path):
                with open(self.keys_file_path, "r") as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.fernet.decrypt(encrypted_data.encode()).decode()
                return json.loads(decrypted_data)
        except (InvalidToken, json.JSONDecodeError, FileNotFoundError):
            # If the file doesn't exist or can't be decrypted, start with an empty dict
            pass
        
        return {}
    
    def _save_keys(self) -> None:
        """Save encryption keys to the keys file."""
        encrypted_data = self.fernet.encrypt(json.dumps(self.keys).encode()).decode()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.keys_file_path)), exist_ok=True)
        
        with open(self.keys_file_path, "w") as f:
            f.write(encrypted_data)
    
    def _generate_new_key(self) -> str:
        """
        Generate a new data encryption key.
        
        Returns:
            Key ID of the new key
        """
        # Generate a new key ID
        key_id = str(uuid.uuid4())
        
        # Generate a random key
        key_bytes = os.urandom(32)  # 256 bits
        key_b64 = base64.urlsafe_b64encode(key_bytes).decode()
        
        # Store the key info
        self.keys[key_id] = {
            "key": key_b64,
            "created_at": int(time.time()),
            "is_current": True,
        }
        
        # Mark other keys as not current
        for other_id, key_info in self.keys.items():
            if other_id != key_id:
                key_info["is_current"] = False
        
        # Save the updated keys
        self._save_keys()
        
        return key_id
    
    def _get_current_key(self) -> Optional[Tuple[str, bytes]]:
        """
        Get the current data encryption key.
        
        Returns:
            Tuple of (key ID, key bytes) or None if no current key
        """
        for key_id, key_info in self.keys.items():
            if key_info.get("is_current", False):
                key_bytes = base64.urlsafe_b64decode(key_info["key"])
                return key_id, key_bytes
        
        return None
    
    def get_key_by_id(self, key_id: str) -> Optional[bytes]:
        """
        Get a key by its ID.
        
        Args:
            key_id: Key ID
            
        Returns:
            Key bytes or None if key not found
        """
        if key_id in self.keys:
            return base64.urlsafe_b64decode(self.keys[key_id]["key"])
        
        return None
    
    def should_rotate_key(self, key_id: str) -> bool:
        """
        Check if a key should be rotated based on its age.
        
        Args:
            key_id: Key ID
            
        Returns:
            True if the key should be rotated, False otherwise
        """
        if key_id not in self.keys:
            return True
        
        key_info = self.keys[key_id]
        created_at = key_info.get("created_at", 0)
        age_days = (int(time.time()) - created_at) / (60 * 60 * 24)
        
        return age_days > self.auto_rotate_days
    
    def rotate_keys(self) -> str:
        """
        Rotate encryption keys by generating a new current key.
        
        Returns:
            Key ID of the new current key
        """
        return self._generate_new_key()

class AES256Cipher:
    """
    AES-256 cipher for encrypting and decrypting data.
    
    Uses AES-256-GCM for authenticated encryption.
    """
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Generate a random AES-256 key.
        
        Returns:
            Random key bytes
        """
        return os.urandom(32)  # 256 bits
    
    @staticmethod
    def encrypt(data: Union[str, bytes], key: bytes) -> Dict[str, str]:
        """
        Encrypt data using AES-256-GCM.
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        if isinstance(data, str):
            data = data.encode()
        
        # Generate a random IV (nonce)
        iv = os.urandom(12)  # 96 bits
        
        # Create the cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt the data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Get the tag
        tag = encryptor.tag
        
        # Encode the results as base64
        iv_b64 = base64.b64encode(iv).decode()
        ciphertext_b64 = base64.b64encode(ciphertext).decode()
        tag_b64 = base64.b64encode(tag).decode()
        
        return {
            "iv": iv_b64,
            "ciphertext": ciphertext_b64,
            "tag": tag_b64,
        }
    
    @staticmethod
    def decrypt(
        encrypted_data: Dict[str, str],
        key: bytes
    ) -> bytes:
        """
        Decrypt data using AES-256-GCM.
        
        Args:
            encrypted_data: Dictionary with encrypted data and metadata
            key: Decryption key
            
        Returns:
            Decrypted data bytes
            
        Raises:
            ValueError: If the data is invalid or authentication fails
        """
        # Decode base64 values
        try:
            iv = base64.b64decode(encrypted_data["iv"])
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            tag = base64.b64decode(encrypted_data["tag"])
        except (KeyError, ValueError):
            raise ValueError("Invalid encrypted data format")
        
        # Create the cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt the data
        try:
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

class Encryptor:
    """
    High-level encryption service with key rotation support.
    
    Uses AES-256-GCM for encrypting data and manages encryption keys.
    """
    
    def __init__(
        self,
        master_key: Optional[str] = None,
        keys_file_path: Optional[str] = None,
        auto_rotate_days: int = 90,
    ):
        """
        Initialize the encryptor.
        
        Args:
            master_key: Master key for encrypting data encryption keys
            keys_file_path: Path to the file storing encrypted keys
            auto_rotate_days: Number of days after which keys should be rotated
        """
        self.key_manager = EncryptionKeyManager(
            master_key=master_key,
            keys_file_path=keys_file_path,
            auto_rotate_days=auto_rotate_days,
        )
    
    def encrypt(self, data: Union[str, bytes]) -> Dict[str, str]:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        # Get the current key
        key_id, key = self.key_manager._get_current_key()
        
        # Check if the key should be rotated
        if self.key_manager.should_rotate_key(key_id):
            key_id = self.key_manager.rotate_keys()
            key = self.key_manager.get_key_by_id(key_id)
        
        # Encrypt the data
        result = AES256Cipher.encrypt(data, key)
        result["key_id"] = key_id
        
        return result
    
    def decrypt(self, encrypted_data: Dict[str, str]) -> bytes:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Dictionary with encrypted data and metadata
            
        Returns:
            Decrypted data bytes
            
        Raises:
            ValueError: If the data is invalid, the key is not found, or authentication fails
        """
        # Get the key ID
        key_id = encrypted_data.get("key_id")
        if not key_id:
            raise ValueError("Key ID not found in encrypted data")
        
        # Get the key
        key = self.key_manager.get_key_by_id(key_id)
        if not key:
            raise ValueError(f"Key with ID {key_id} not found")
        
        # Decrypt the data
        return AES256Cipher.decrypt(encrypted_data, key)
    
    def rotate_keys(self) -> None:
        """Rotate encryption keys."""
        self.key_manager.rotate_keys()

# Helper functions for simple encryption/decryption
def encrypt_string(text: str, master_key: Optional[str] = None) -> str:
    """
    Encrypt a string.
    
    Args:
        text: String to encrypt
        master_key: Optional master key
        
    Returns:
        JSON string with encrypted data
    """
    encryptor = Encryptor(master_key=master_key)
    result = encryptor.encrypt(text)
    return json.dumps(result)

def decrypt_string(encrypted_json: str, master_key: Optional[str] = None) -> str:
    """
    Decrypt a string.
    
    Args:
        encrypted_json: JSON string with encrypted data
        master_key: Optional master key
        
    Returns:
        Decrypted string
        
    Raises:
        ValueError: If decryption fails
    """
    encryptor = Encryptor(master_key=master_key)
    encrypted_data = json.loads(encrypted_json)
    decrypted = encryptor.decrypt(encrypted_data)
    return decrypted.decode()

def secure_hash(data: Union[str, bytes]) -> str:
    """
    Create a secure hash of data.
    
    Args:
        data: Data to hash
        
    Returns:
        Secure hash as a hex string
    """
    if isinstance(data, str):
        data = data.encode()
    
    return hashlib.sha256(data).hexdigest()

def hmac_sign(data: Union[str, bytes], key: Union[str, bytes]) -> str:
    """
    Create an HMAC signature for data.
    
    Args:
        data: Data to sign
        key: Signing key
        
    Returns:
        HMAC signature as a hex string
    """
    if isinstance(data, str):
        data = data.encode()
    
    if isinstance(key, str):
        key = key.encode()
    
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    return h.finalize().hex()

def hmac_verify(
    data: Union[str, bytes],
    signature: str,
    key: Union[str, bytes]
) -> bool:
    """
    Verify an HMAC signature for data.
    
    Args:
        data: Data to verify
        signature: HMAC signature as a hex string
        key: Signing key
        
    Returns:
        True if the signature is valid, False otherwise
    """
    if isinstance(data, str):
        data = data.encode()
    
    if isinstance(key, str):
        key = key.encode()
    
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    
    try:
        h.verify(bytes.fromhex(signature))
        return True
    except Exception:
        return False
