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

def _run_jira_generation(issue_keys_raw: str, prd_file=None):
    """Call /generate/jira and display the result. issue_keys_raw is comma-separated."""
    parsed = [k.strip() for k in issue_keys_raw.split(",") if k.strip()]
    label = ", ".join(parsed)
    with st.spinner(f"⚙️ Generating from JIRA issue(s): {label}..."):
        try:
            # Derive project name from the first key
            first_key = parsed[0] if parsed else "project"
            form_data = {
                "issue_keys": (None, issue_keys_raw),
                "project_name": (None, first_key.replace("-", "_").lower()),
            }
            # Include user-supplied credentials if provided in sidebar
            jira_url = st.session_state.get("jira_url", "").strip()
            jira_email = st.session_state.get("jira_email", "").strip()
            jira_token = st.session_state.get("jira_token", "").strip()
            if jira_url:
                form_data["jira_url"] = (None, jira_url)
            if jira_email:
                form_data["jira_email"] = (None, jira_email)
            if jira_token:
                form_data["jira_token"] = (None, jira_token)
            if prd_file:
                form_data["file"] = (prd_file.name, prd_file.read(), "application/octet-stream")
            response = requests.post(
                f"{API_BASE_URL}/generate/jira",
                files=form_data,
                timeout=300,
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Make sure the FastAPI backend is running.")
            return
        except requests.exceptions.HTTPError:
            st.error(f"API error {response.status_code}: {response.text}")
            return
        except Exception as e:
            st.error(f"Request failed: {str(e)}")
            return
    _show_generation_result(result)


def _show_generation_result(result):
    """Render the download button and file list for a completed generation."""
    if not result or "zip_file" not in result:
        st.error("Generation did not return a zip file.")
        return

    zip_path = result["zip_file"]
    if not os.path.exists(zip_path):
        st.error("Generated zip file not found on server.")
        return

    with open(zip_path, "rb") as f:
        zip_data = f.read()

    st.success("✅ Code generation completed!")
    st.download_button(
        label="📦 Download Generated Code",
        data=zip_data,
        file_name="generated_spring_boot_app.zip",
        mime="application/zip",
        use_container_width=True,
    )

    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        file_list = zf.namelist()
        st.subheader("📁 Generated Files")
        for fname in sorted(file_list)[:20]:
            st.code(fname, language=None)
        if len(file_list) > 20:
            st.text(f"... and {len(file_list) - 20} more files")


def main():

    # ── Sidebar: JIRA credentials ──────────────────────────────────────────────
    with st.sidebar:
        st.header("JIRA Configuration")
        st.caption(
            "Enter your own credentials here. Leave blank to use the server's "
            "environment variables (single-user / self-hosted setup)."
        )
        st.session_state.jira_url = st.text_input(
            "JIRA Base URL",
            value=st.session_state.get("jira_url", ""),
            placeholder="https://yourcompany.atlassian.net",
        )
        st.session_state.jira_email = st.text_input(
            "Email",
            value=st.session_state.get("jira_email", ""),
            placeholder="you@company.com",
        )
        st.session_state.jira_token = st.text_input(
            "API Token",
            value=st.session_state.get("jira_token", ""),
            type="password",
            placeholder="Your Atlassian API token",
            help="Generate one at id.atlassian.com → Security → API tokens",
        )
        if all([
            st.session_state.get("jira_url"),
            st.session_state.get("jira_email"),
            st.session_state.get("jira_token"),
        ]):
            st.success("Credentials set")
        else:
            st.info("Using server environment credentials")

    st.title("🚀 AI Code Generator")
    st.markdown("Generate Spring Boot applications from Product Requirements Documents (PRDs)")

    # Main content
    with st.container():
        st.header("📄 PRD Input")

        # PRD input methods
        input_method = st.radio(
            "Choose input method:",
            ["File Upload", "JIRA Issue"],
            horizontal=True
        )

        uploaded_file = None
        prd_text = ""
        jira_issue_key = ""
        jira_prd_file = None

        if input_method == "File Upload":
            uploaded_file = st.file_uploader(
                "Upload PRD document:",
                type=["txt", "md", "docx", "doc", "pdf"],
                help="Upload a PRD document"
            )

            if uploaded_file:
                file_type = uploaded_file.name.split(".")[-1].lower()
                try:
                    if file_type in ["txt", "md"]:
                        file_bytes = uploaded_file.read()
                        for encoding in ["utf-8", "utf-16", "latin-1", "cp1252"]:
                            try:
                                prd_text = file_bytes.decode(encoding)
                                break
                            except UnicodeDecodeError:
                                continue
                        if not prd_text:
                            st.error("Could not decode text file. Please use UTF-8 encoded files.")

                    elif file_type == "docx":
                        doc = Document(uploaded_file)
                        prd_text = "\n".join(para.text for para in doc.paragraphs)

                    elif file_type == "pdf":
                        pdf_reader = PdfReader(uploaded_file)
                        prd_text = "\n".join(
                            page.extract_text() for page in pdf_reader.pages
                            if page.extract_text()
                        )

                    elif file_type == "doc":
                        st.warning(".doc format is not fully supported. Please convert to .docx.")

                    else:
                        st.error("Unsupported file type.")

                    if prd_text:
                        st.text_area(
                            "File content preview:",
                            prd_text[:500] + "..." if len(prd_text) > 500 else prd_text,
                            height=200,
                            disabled=True,
                        )
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")

            st.markdown("---")
            jira_issue_key = st.text_input(
                "JIRA Issue Key(s) (optional — supplements the PRD)",
                placeholder="e.g. PROJ-123 or PROJ-123, PROJ-124",
            ).strip()
            if jira_issue_key:
                st.caption("JIRA issue content and sprint context will be merged with the PRD file.")

        else:  # JIRA Issue only
            st.markdown("Enter one or more JIRA issue keys (comma-separated). Their descriptions and sprint context will be used as requirements.")
            jira_issue_key = st.text_input(
                "JIRA Issue Key(s)",
                placeholder="PROJ-123 or PROJ-123, PROJ-124, PROJ-125",
            ).strip()
            st.markdown("---")
            jira_prd_file = st.file_uploader(
                "PRD document (optional — merged with JIRA content)",
                type=["txt", "md", "docx", "pdf"],
                help="When provided, its content is appended to the JIRA issue requirements.",
            )

        # Generate button
        if st.button("🚀 Generate Code", type="primary", use_container_width=True):

            # ── JIRA-only path ─────────────────────────────────────────────────
            if input_method == "JIRA Issue":
                if not jira_issue_key:
                    st.error("Please enter at least one JIRA issue key.")
                    return
                _run_jira_generation(jira_issue_key, prd_file=jira_prd_file)
                return

            # ── File Upload path ───────────────────────────────────────────────
            if not uploaded_file and not jira_issue_key:
                st.error("Please upload a PRD file or enter a JIRA issue key.")
                return

            if jira_issue_key:
                # PRD file + JIRA key → JIRA pipeline (file is supplementary)
                # Reset stream position — file may have been read during preview
                if uploaded_file:
                    uploaded_file.seek(0)
                _run_jira_generation(jira_issue_key, prd_file=uploaded_file)
            else:
                # PRD file only → standard pipeline
                if not prd_text.strip():
                    st.error("Could not read content from the uploaded file.")
                    return
                with st.spinner("🔍 Analyzing requirements..."):
                    call_api("/mcp/context", "POST", {"requirements": prd_text})
                with st.spinner("⚙️ Generating Spring Boot application..."):
                    result = None
                    temp_file_path = None
                    temp_file = tempfile.NamedTemporaryFile(
                        mode="w", suffix=".txt", delete=False, encoding="utf-8"
                    )
                    try:
                        temp_file.write(prd_text)
                        temp_file.close()
                        temp_file_path = temp_file.name
                        with open(temp_file_path, "rb") as f:
                            result = call_api("/generate", "POST", files={"file": ("prd.txt", f, "text/plain")})
                    finally:
                        if temp_file_path and os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)
                    _show_generation_result(result)

    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit, FastAPI, and AI-powered code generation")

if __name__ == "__main__":
    main()