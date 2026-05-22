import streamlit as st
import os
import base64
from pathlib import Path
from crypto_utils import encrypt_file, decrypt_file, generate_key_from_password
from file_manager import save_hidden_file, get_hidden_files, delete_hidden_file

# Create hidden directory if it doesn't exist
HIDDEN_DIR = "hidden_files"
os.makedirs(HIDDEN_DIR, exist_ok=True)

def main():
    st.title("🔒 Secure Media Hiding System")
    st.markdown("Encrypt and hide your sensitive images and videos securely.")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    mode = st.sidebar.radio("Select Mode", ["Hide Media", "Retrieve Media", "Manage Hidden Files"])
    
    if mode == "Hide Media":
        hide_media_interface()
    elif mode == "Retrieve Media":
        retrieve_media_interface()
    else:
        manage_hidden_files_interface()

def hide_media_interface():
    st.header("📁 Hide Media Files")
    st.markdown("Upload and encrypt your sensitive media files.")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a media file",
        type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mkv', 'webm'],
        help="Supported formats: Images (JPG, PNG, GIF) and Videos (MP4, AVI, MOV, MKV, WEBM)"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Security key input
        security_key = st.text_input(
            "🔑 Enter Security Key",
            type="password",
            help="This key will be required to retrieve your hidden file"
        )
        
        # Optional description
        description = st.text_input(
            "📝 Description (Optional)",
            help="Add a description to help identify this file later"
        )
        
        if st.button("🔒 Hide File", type="primary"):
            if not security_key:
                st.error("❌ Security key is required!")
                return
            
            if len(security_key) < 4:
                st.error("❌ Security key must be at least 4 characters long!")
                return
            
            try:
                with st.spinner("🔄 Encrypting and hiding file..."):
                    # Read file content
                    file_content = uploaded_file.read()
                    
                    # Generate encryption key from password
                    encryption_key = generate_key_from_password(security_key)
                    
                    # Encrypt file content
                    encrypted_content = encrypt_file(file_content, encryption_key)
                    
                    # Save hidden file
                    hidden_filename = save_hidden_file(
                        encrypted_content,
                        uploaded_file.name,
                        description or "No description"
                    )
                    
                    st.success(f"✅ File successfully hidden as: {hidden_filename}")
                    st.info("💡 Remember your security key - it cannot be recovered!")
                    
            except Exception as e:
                st.error(f"❌ Error hiding file: {str(e)}")

def retrieve_media_interface():
    st.header("🔓 Retrieve Hidden Files")
    st.markdown("Enter your security key to decrypt and download your hidden files.")
    
    # Get list of hidden files
    hidden_files = get_hidden_files()
    
    if not hidden_files:
        st.warning("📭 No hidden files found.")
        return
    
    # Create options for selectbox
    file_options = {}
    for filename, info in hidden_files.items():
        display_name = f"{info['original_name']} - {info['description']}"
        file_options[display_name] = filename
    
    # File selection
    selected_display = st.selectbox(
        "📂 Select Hidden File",
        options=list(file_options.keys()),
        help="Choose the file you want to retrieve"
    )
    
    if selected_display:
        selected_file = file_options[selected_display]
        file_info = hidden_files[selected_file]
        
        # Display file info
        st.info(f"📄 Original Name: {file_info['original_name']}")
        st.info(f"📝 Description: {file_info['description']}")
        st.info(f"📅 Hidden On: {file_info['timestamp']}")
        
        # Security key input
        security_key = st.text_input(
            "🔑 Enter Security Key",
            type="password",
            help="Enter the key you used to hide this file"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔓 Retrieve File", type="primary"):
                if not security_key:
                    st.error("❌ Security key is required!")
                    return
                
                try:
                    with st.spinner("🔄 Decrypting file..."):
                        # Read encrypted file
                        hidden_path = os.path.join(HIDDEN_DIR, selected_file)
                        with open(hidden_path, 'rb') as f:
                            encrypted_content = f.read()
                        
                        # Generate decryption key
                        decryption_key = generate_key_from_password(security_key)
                        
                        # Decrypt file
                        decrypted_content = decrypt_file(encrypted_content, decryption_key)
                        
                        # Prepare download
                        b64_content = base64.b64encode(decrypted_content).decode()
                        
                        st.success("✅ File successfully decrypted!")
                        
                        # Download button
                        st.download_button(
                            label="💾 Download Original File",
                            data=decrypted_content,
                            file_name=file_info['original_name'],
                            mime="application/octet-stream"
                        )
                        
                        # Display preview for images
                        if file_info['original_name'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            st.image(decrypted_content, caption=file_info['original_name'])
                        
                except Exception as e:
                    st.error(f"❌ Failed to decrypt file. Check your security key. Error: {str(e)}")
        
        with col2:
            if st.button("🗑️ Delete Hidden File", type="secondary"):
                if st.button("⚠️ Confirm Delete", key="confirm_delete"):
                    try:
                        delete_hidden_file(selected_file)
                        st.success("✅ Hidden file deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting file: {str(e)}")

def manage_hidden_files_interface():
    st.header("📊 Manage Hidden Files")
    st.markdown("Overview of all your hidden files.")
    
    hidden_files = get_hidden_files()
    
    if not hidden_files:
        st.warning("📭 No hidden files found.")
        return
    
    st.subheader(f"📂 Total Hidden Files: {len(hidden_files)}")
    
    # Display files in a table-like format
    for filename, info in hidden_files.items():
        with st.expander(f"📄 {info['original_name']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Original Name:** {info['original_name']}")
                st.write(f"**Description:** {info['description']}")
                st.write(f"**Hidden On:** {info['timestamp']}")
            
            with col2:
                st.write(f"**Hidden Filename:** {filename}")
                
                # Get file size
                hidden_path = os.path.join(HIDDEN_DIR, filename)
                if os.path.exists(hidden_path):
                    file_size = os.path.getsize(hidden_path)
                    st.write(f"**Encrypted Size:** {file_size} bytes")
                
                if st.button(f"🗑️ Delete {filename}", key=f"del_{filename}"):
                    try:
                        delete_hidden_file(filename)
                        st.success("✅ File deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting file: {str(e)}")

if __name__ == "__main__":
    main()
