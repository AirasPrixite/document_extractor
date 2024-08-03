import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import io
import base64
from dotenv import load_dotenv
import os
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment
api_key = os.getenv('ANTHROPIC_API_KEY')

# Initialize the Anthropic client with the API key
client = Anthropic(api_key=api_key)
MODEL_NAME = "claude-3-opus-20240229"

invoice_tool = {
    "name": "print_invoice_info",
    "description": "Extracts required fields from an invoice image.",
    "input_schema": {
        "type": "object",
        "properties": {
            "account_no": {"type": "integer", "description": "The account number of a bank"},
            "currency": {"type": "integer", "description": "The currency used for dealing"},
            "email": {"type": "string", "description": "The email address used for communication"},
            "gst_no": {"type": "integer", "description": "The tax number of the merchant/supplier"},
            "invoice_number": {"type": "integer", "description": "The number of invoice"},
            "issue_date": {"type": "string", "description": "The date of issuing the invoice"},
            "merchant_address": {"type": "string", "description": "The address of the merchant"}, 
            "merchant_name": {"type": "string", "description": "The number of the merchant"}, 
            "phone": {"type": "integer", "description": "The phone number of the merchant"}, 
            "po_number": {"type": "integer", "description": "The purchase order number against which the invoice is generated"}, 
            "supplier_address": {"type": "string", "description": "The address of the supplier"}, 
            "supplier_name": {"type": "string", "description": "The name of the supplier"}, 
            "tax_amount": {"type": "integer", "description": "The amount of tax charged on the invoice"}, 
            "tax_percent": {"type": "string", "description": "The percentage of tax applicable on the invoice"}, 
            "terms": {"type": "string", "description": "The terms of purchase mentioned on the invoice"}, 
            "total": {"type": "integer", "description": "The total amount mentioned on the invoice"}, 
            "merchant_id": {"type": "string", "description": "The id of the merchant"}, 
            "supplier_id": {"type": "string", "description": "The id of the supplier"}
        },
        "required": ["account_no", "currency", "email", "gst_no", "invoice_number", "issue_date", "merchant_address", "merchant_name", "phone", "po_number", "supplier_address", "supplier_name", "tax_amount", "tax_percent", "terms", "total", "merchant_id", "supplier_id"]
    }
}

soa_tool = {
    "name": "print_soa_info",
    "description": "Extracts required fields from a statement of accounts image.",
    "input_schema": {
        "type": "object",
        "properties": {
            "conversion_rate": {"type": "string", "description": "The conversion rate on the statement of account"},
            "currency_code": {"type": "string", "description": "The code of the currency used"},
            "document_status": {"type": "string", "description": "Status of the document"},
            "invoice_end_date": {"type": "string", "description": "End date of the invoice"},
            "invoice_start_date": {"type": "string", "description": "Start date of the invoice"},
            "issue_date_time": {"type": "string", "description": "Date and time on which the invoice was issued"},
            "merchant_id": {"type": "string", "description": "ID of the merchant"}, 
            "merchant_name": {"type": "string", "description": "The name of the merchant"}, 
            "value": {"type": "string", "description": "Value of the statement of account"}, 
            "remarks": {"type": "string", "description": "Any remarks about the statement of account"}, 
            "statement_date": {"type": "string", "description": "Date of the statement of account"}, 
            "statement_of_account_lines": {"type": "string", "description": "The lines mentioned on the statement of account"}, 
            "supplier_id": {"type": "string", "description": "ID of the supplier"}, 
            "supplier_name": {"type": "string", "description": "The name of the supplier"}
        },
        "required": ["conversion_rate", "currency_code", "document_status", "invoice_end_date", "invoice_start_date",
                     "issue_date_time", "merchant_id", "merchant_name", "value", "remarks",
                     "statement_date", "statement_of_account_lines", "supplier_id", "supplier_name"]
    }
}

credit_note_tool = {
    "name": "print_credit_note_info",
    "description": "Extracts required fields from a credit note image.",
    "input_schema": {
        "type": "object",
        "properties": {
            "conversion_rate": {"type": "string", "description": "The conversion rate on the credit note"},
            "credit_note_items": {"type": "string", "description": "The items listed on the credit note"},
            "credit_note_number": {"type": "string", "description": "The number of the credit note"},
            "currency_code": {"type": "string", "description": "The currency code of the currency used"},
            "document_status": {"type": "string", "description": "Status of the document"},
            "due_date": {"type": "string", "description": "Date on which the credit note is due"},
            "invoice_number": {"type": "string", "description": "Number of the invoice"}, 
            "issue_date_time": {"type": "string", "description": "The date and time of when the credit note was issued."}, 
            "merchant_id": {"type": "string", "description": "ID of the merchant"}, 
            "merchant_name": {"type": "string", "description": "Name of the merchant"}, 
            "receipt_number": {"type": "string", "description": "Number of the receipt"}, 
            "remarks": {"type": "string", "description": "Any remarks added to the credit note"}, 
            "supplier_id": {"type": "string", "description": "ID of the supplier"}, 
            "supplier_name": {"type": "string", "description": "The name of the supplier"}, 
            "total_tax_amount": {"type": "string", "description": "The total amount of tax"}
        },
        "required": ["conversion_rate", "credit_note_items", "credit_note_number", 
                     "currency_code", "document_status", "due_date", "invoice_number", "issue_date_time", 
                     "merchant_id", "merchant_name", "receipt_number", "remarks", "supplier_id", 
                     "supplier_name", "total_tax_amount"]
    }
}

def convert_pdf_to_jpeg(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img_bytes = io.BytesIO(pix.tobytes())
        image = Image.open(img_bytes)
        jpeg_bytes = io.BytesIO()
        image.convert("RGB").save(jpeg_bytes, format="JPEG")
        jpeg_bytes.seek(0)
        images.append(Image.open(jpeg_bytes))
    return images

def convert_png_to_jpeg(png_file):
    image = Image.open(png_file)
    jpeg_bytes = io.BytesIO()
    image.convert("RGB").save(jpeg_bytes, format="JPEG")
    jpeg_bytes.seek(0)
    return Image.open(jpeg_bytes)

def get_base64_encoded_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    base64_encoded_data = base64.b64encode(buffered.getvalue())
    return base64_encoded_data.decode('utf-8')

st.title("Document Upload and Type Selection")

document_type_options = ["Statement of Account", "Credit Note", "Invoice"]
document_type = st.selectbox("Select the type of document", document_type_options)

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.subheader("File Details")
    st.write(f"**File Name:** {uploaded_file.name}")
    st.write(f"**Document Type:** {document_type}")

    images = []
    if uploaded_file.type == "application/pdf":
        images = convert_pdf_to_jpeg(uploaded_file)
        for img in images:
            st.image(img, caption="Converted JPEG from PDF")
    elif uploaded_file.type == "image/png":
        jpeg_file = convert_png_to_jpeg(uploaded_file)
        st.image(jpeg_file, caption="Converted JPEG from PNG")
        images.append(jpeg_file)
    elif uploaded_file.type in ["image/jpeg", "image/jpg"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded JPEG Image")
        images.append(image)

    if document_type == "Invoice":
        st.write("Processing Invoice...")
        for img in images:
            base64_image = get_base64_encoded_image(img)
            message_list = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}},
                        {"type": "text", "text": "Please print the required fields from the invoice provided."}
                    ]
                }
            ]
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=4096,
                messages=message_list,
                tools=[invoice_tool]
            )
            if response.stop_reason == "tool_use":
                last_content_block = response.content[-1]
                if last_content_block.type == 'tool_use':
                    tool_name = last_content_block.name
                    tool_inputs = last_content_block.input
                    st.write(f"=======Claude Wants To Call The {tool_name} Tool=======")
                    st.write(tool_inputs)
            else:
                st.write("No tool was called. This shouldn't happen!")
    elif document_type == "Statement of Account":
        st.write("Processing Statement of Account...")
        for img in images:
            base64_image = get_base64_encoded_image(img)
            message_list = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}},
                        {"type": "text", "text": "Please print the required fields from the statement of account provided."}
                    ]
                }
            ]
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=4096,
                messages=message_list,
                tools=[soa_tool]
            )
            if response.stop_reason == "tool_use":
                last_content_block = response.content[-1]
                if last_content_block.type == 'tool_use':
                    tool_name = last_content_block.name
                    tool_inputs = last_content_block.input
                    st.write(f"=======Claude Wants To Call The {tool_name} Tool=======")
                    st.write(tool_inputs)
            else:
                st.write("No tool was called. This shouldn't happen!")
    elif document_type == "Credit Note":
        st.write("Processing Credit Note...")
        for img in images:
            base64_image = get_base64_encoded_image(img)
            message_list = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}},
                        {"type": "text", "text": "Please print the required fields from the credit note provided."}
                    ]
                }
            ]
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=4096,
                messages=message_list,
                tools=[credit_note_tool]
            )
            if response.stop_reason == "tool_use":
                last_content_block = response.content[-1]
                if last_content_block.type == 'tool_use':
                    tool_name = last_content_block.name
                    tool_inputs = last_content_block.input
                    st.write(f"=======Claude Wants To Call The {tool_name} Tool=======")
                    st.write(tool_inputs)
            else:
                st.write("No tool was called. This shouldn't happen!")
    else:
        st.write("Other tools building in progress on the frontend")
