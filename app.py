import pathlib

import streamlit as st

from logdata import LogData


FILES_DIR = pathlib.Path("files")
OUTPUT_DIR = pathlib.Path("data")


def _save_upload(uploaded_file) -> pathlib.Path:
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    destination = FILES_DIR / uploaded_file.name
    destination.write_bytes(uploaded_file.getbuffer())
    return destination


st.set_page_config(page_title="Your Web Shield", page_icon="🛡️", layout="centered")
st.title("🛡️ Your Web Shield")
st.write("Upload a web server log file and run analysis in one click.")

uploaded_file = st.file_uploader(
    "Upload a log file",
    type=["txt", "log"],
    help="Example: your-site-ssl_log-Aug-2023.txt",
)

if st.button("Analyze uploaded file", type="primary", disabled=uploaded_file is None):
    if uploaded_file is None:
        st.warning("Please upload a file first.")
    else:
        with st.spinner("Saving file and running analysis..."):
            saved_path = _save_upload(uploaded_file)
            LogData(saved_path.name)
        st.success(f"Analysis complete for `{saved_path.name}`")

if OUTPUT_DIR.exists():
    output_files = sorted([p for p in OUTPUT_DIR.iterdir() if p.is_file()])
    if output_files:
        st.subheader("Generated output files")
        for output_file in output_files:
            with output_file.open("rb") as handle:
                st.download_button(
                    label=f"Download {output_file.name}",
                    data=handle.read(),
                    file_name=output_file.name,
                    mime="text/plain",
                )
