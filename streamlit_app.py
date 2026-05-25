import streamlit as st
import requests
import zipfile
import io
import os
import tempfile
from docx import Document
from PyPDF2 import PdfReader
import io

# Configure page
st.set_page_config(
    page_title="AI Code Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

def call_api(endpoint: str, method: str = "GET", data: dict = None, files: dict = None):
    """Call FastAPI backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=360)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, timeout=360)
            else:
                response = requests.post(url, json=data, timeout=360)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to API at {API_BASE_URL}. Make sure the FastAPI backend is running.")
        return None
    except requests.exceptions.Timeout:
        st.error(f"❌ API request timed out. The backend may be overloaded.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API returned error {response.status_code}: {response.text}")
        return None
    except Exception as e:
        st.error(f"❌ API call failed: {str(e)}")
        return None

def main():

    st.title("🚀 AI Code Generator")
    st.markdown("Generate Spring Boot applications from Product Requirements Documents (PRDs)")

    # Main content
    with st.container():
        st.header("📄 PRD Input")

        # PRD input methods
        input_method = st.radio(
            "Choose input method:",
            ["Text Input", "File Upload"],
            horizontal=True
        )

        prd_text = ""

        if input_method == "Text Input":
            prd_text = st.text_area(
                "Enter your Product Requirements Document:",
                height=300,
                placeholder="""Describe your application requirements here...

    Example:
    Create a user management system with login, registration, and profile management features.
    Users should have name, email, and role fields."""
            )

        else:
            uploaded_file = st.file_uploader(
                "Upload PRD document:",
                type=["txt", "md", "docx", "doc", "pdf"],
                help="Upload a PRD document"
            )

            if uploaded_file:

                file_type = uploaded_file.name.split(".")[-1].lower()

                try:
                    # TXT / MD
                    if file_type in ["txt", "md"]:

                        file_bytes = uploaded_file.read()

                        encodings = ["utf-8", "utf-16", "latin-1", "cp1252"]

                        for encoding in encodings:
                            try:
                                prd_text = file_bytes.decode(encoding)
                                break
                            except UnicodeDecodeError:
                                continue

                        if not prd_text:
                            st.error("Could not decode text file. Please use UTF-8 encoded files.")

                    # DOCX
                    elif file_type == "docx":
                        doc = Document(uploaded_file)

                        paragraphs = []
                        for para in doc.paragraphs:
                            paragraphs.append(para.text)

                        prd_text = "\n".join(paragraphs)

                    # PDF
                    elif file_type == "pdf":
                        pdf_reader = PdfReader(uploaded_file)

                        text = []
                        for page in pdf_reader.pages:
                            extracted = page.extract_text()
                            if extracted:
                                text.append(extracted)

                        prd_text = "\n".join(text)

                    # DOC (legacy Word format)
                    elif file_type == "doc":
                        st.warning(
                            ".doc format is not fully supported. "
                            "Please convert it to .docx for best results."
                        )

                    else:
                        st.error("Unsupported file type.")

                    # Preview content
                    if prd_text:
                        st.text_area(
                            "File content preview:",
                            prd_text[:500] + "..." if len(prd_text) > 500 else prd_text,
                            height=200,
                            disabled=True
                        )

                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")

        # Generate button
        if st.button("🚀 Generate Code", type="primary", use_container_width=True):
            if not prd_text.strip():
                st.error("Please provide PRD content first!")
                return

            with st.spinner("🔍 Analyzing requirements..."):
                # Get MCP context first
                context_result = call_api("/mcp/context", "POST", {"requirements": prd_text})
                if context_result:
                    context = context_result.get("context", "").strip()
                    # if context:
                    #     st.success("✅ MCP context loaded")
                    #     with st.expander("MCP Context overview", expanded=False):
                    #         st.write(context)
                    # else:
                    #     st.warning("MCP did not return context text.")

            with st.spinner("⚙️ Generating Spring Boot application..."):
                # Create temporary file for API
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                try:
                    temp_file.write(prd_text)
                    temp_file.close()
                    temp_file_path = temp_file.name

                    # Call the generate endpoint
                    with open(temp_file_path, 'rb') as f:
                        files = {'file': ('prd.txt', f, 'text/plain')}
                        result = call_api("/generate", "POST", files=files)

                    if result and "zip_file" in result:
                        zip_path = result["zip_file"]

                        # Read and provide download
                        if os.path.exists(zip_path):
                            with open(zip_path, "rb") as f:
                                zip_data = f.read()

                            st.success("✅ Code generation completed!")
                            st.download_button(
                                label="📦 Download Generated Code",
                                data=zip_data,
                                file_name="generated_spring_boot_app.zip",
                                mime="application/zip",
                                use_container_width=True
                            )

                            # Show zip contents
                            with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                                file_list = zf.namelist()
                                st.subheader("📁 Generated Files")
                                for file in sorted(file_list)[:20]:  # Show first 20 files
                                    st.code(file, language=None)
                                if len(file_list) > 20:
                                    st.text(f"... and {len(file_list) - 20} more files")

                        else:
                            st.error("Generated zip file not found")

                finally:
                    # Clean up temp file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit, FastAPI, and AI-powered code generation")

if __name__ == "__main__":
    main()