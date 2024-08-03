import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import io

def convert_pdf_to_jpeg(pdf_file):
    # Open the PDF and convert the first page to an image
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    first_page = pdf_document.load_page(0)
    pix = first_page.get_pixmap()
    img_bytes = io.BytesIO(pix.tobytes())
    image = Image.open(img_bytes)
    
    # Convert the image to JPEG
    jpeg_bytes = io.BytesIO()
    image.convert("RGB").save(jpeg_bytes, format="JPEG")
    jpeg_bytes.seek(0)
    return jpeg_bytes

def convert_png_to_jpeg(png_file):
    # Open the PNG image
    image = Image.open(png_file)
    
    # Convert the image to JPEG
    jpeg_bytes = io.BytesIO()
    image.convert("RGB").save(jpeg_bytes, format="JPEG")
    jpeg_bytes.seek(0)
    return jpeg_bytes

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
        # Convert PDF to JPEG
        jpeg_file = convert_pdf_to_jpeg(uploaded_file)
        st.image(jpeg_file, caption="Converted JPEG from PDF")
    elif uploaded_file.type == "image/png":
        # Convert PNG to JPEG
        jpeg_file = convert_png_to_jpeg(uploaded_file)
        st.image(jpeg_file, caption="Converted JPEG from PNG")
    elif uploaded_file.type in ["image/jpeg", "image/jpg"]:
        # Display the uploaded JPEG image directly
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded JPEG Image")
