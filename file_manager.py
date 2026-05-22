import os
import json
import datetime
from typing import Dict, Any
from crypto_utils import obfuscate_filename

HIDDEN_DIR = "hidden_files"
METADATA_FILE = os.path.join(HIDDEN_DIR, ".metadata.json")

def load_metadata() -> Dict[str, Any]:
    """
    Load metadata about hidden files.
    
    Returns:
        Dict: Metadata dictionary
    """
    try:
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

def save_metadata(metadata: Dict[str, Any]) -> None:
    """
    Save metadata about hidden files.
    
    Args:
        metadata (Dict): Metadata to save
    """
    try:
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save metadata: {str(e)}")

def save_hidden_file(encrypted_content: bytes, original_name: str, description: str) -> str:
    """
    Save an encrypted file with obfuscated name and update metadata.
    
    Args:
        encrypted_content (bytes): Encrypted file content
        original_name (str): Original filename
        description (str): File description
    
    Returns:
        str: The obfuscated filename
    """
    try:
        # Generate obfuscated filename
        hidden_filename = obfuscate_filename(original_name)
        
        # Ensure unique filename
        counter = 1
        base_hidden_filename = hidden_filename
        while os.path.exists(os.path.join(HIDDEN_DIR, hidden_filename)):
            name_part, ext_part = os.path.splitext(base_hidden_filename)
            hidden_filename = f"{name_part}_{counter}{ext_part}"
            counter += 1
        
        # Save encrypted file
        hidden_path = os.path.join(HIDDEN_DIR, hidden_filename)
        with open(hidden_path, 'wb') as f:
            f.write(encrypted_content)
        
        # Update metadata
        metadata = load_metadata()
        metadata[hidden_filename] = {
            'original_name': original_name,
            'description': description,
            'timestamp': datetime.datetime.now().isoformat(),
            'size': len(encrypted_content)
        }
        save_metadata(metadata)
        
        return hidden_filename
    
    except Exception as e:
        raise Exception(f"Failed to save hidden file: {str(e)}")

def get_hidden_files() -> Dict[str, Any]:
    """
    Get information about all hidden files.
    
    Returns:
        Dict: Dictionary of hidden files and their metadata
    """
    try:
        metadata = load_metadata()
        
        # Filter out files that no longer exist
        existing_files = {}
        for filename, info in metadata.items():
            hidden_path = os.path.join(HIDDEN_DIR, filename)
            if os.path.exists(hidden_path):
                existing_files[filename] = info
        
        # Update metadata if some files were removed
        if len(existing_files) != len(metadata):
            save_metadata(existing_files)
        
        return existing_files
    
    except Exception:
        return {}

def delete_hidden_file(hidden_filename: str) -> None:
    """
    Delete a hidden file and remove it from metadata.
    
    Args:
        hidden_filename (str): The obfuscated filename to delete
    """
    try:
        # Delete the file
        hidden_path = os.path.join(HIDDEN_DIR, hidden_filename)
        if os.path.exists(hidden_path):
            os.remove(hidden_path)
        
        # Update metadata
        metadata = load_metadata()
        if hidden_filename in metadata:
            del metadata[hidden_filename]
            save_metadata(metadata)
    
    except Exception as e:
        raise Exception(f"Failed to delete hidden file: {str(e)}")

def get_hidden_file_content(hidden_filename: str) -> bytes:
    """
    Read the content of a hidden file.
    
    Args:
        hidden_filename (str): The obfuscated filename
    
    Returns:
        bytes: File content
    """
    try:
        hidden_path = os.path.join(HIDDEN_DIR, hidden_filename)
        with open(hidden_path, 'rb') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Failed to read hidden file: {str(e)}")

def cleanup_orphaned_files() -> None:
    """
    Remove files in hidden directory that are not in metadata.
    """
    try:
        metadata = load_metadata()
        
        if not os.path.exists(HIDDEN_DIR):
            return
        
        for filename in os.listdir(HIDDEN_DIR):
            if filename == ".metadata.json":
                continue
            
            if filename not in metadata:
                orphaned_path = os.path.join(HIDDEN_DIR, filename)
                if os.path.isfile(orphaned_path):
                    os.remove(orphaned_path)
    
    except Exception:
        pass  # Silently handle cleanup errors
