import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import io
import os

st.title("Document Upload and Type Selection")

# Dropdown for selecting document type
document_type_options = ["Statement of Account", "Credit Note", "Invoice"]
document_type = st.selectbox("Select the type of document", document_type_options)

# File uploader for images or PDFs
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    # Display file details
    st.subheader("File Details")
    st.write(f"**File Name:** {uploaded_file.name}")
    st.write(f"**Document Type:** {document_type}")

    # Process the uploaded file based on type
    if uploaded_file.type == "application/pdf":
        # Display first page of PDF as an image
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        first_page = doc.load_page(0)
        pix = first_page.get_pixmap()
        img_bytes = io.BytesIO(pix.tobytes())
        image = Image.open(img_bytes)
        st.image(image, caption="First page of the PDF")
    else:
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")
