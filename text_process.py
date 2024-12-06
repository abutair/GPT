import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.exceptions import HttpResponseError
import PyPDF2

# Azure Document Intelligence endpoint and key
endpoint = "https://abutair-ocr.cognitiveservices.azure.com/"
key = "5ee769d36dbb4399a3ef104075f7195f"


# Initialize the client
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

def split_pdf(input_pdf, output_prefix, max_pages=10):
    with open(input_pdf, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)
        
        for i in range(0, total_pages, max_pages):
            writer = PyPDF2.PdfWriter()
            for j in range(i, min(i + max_pages, total_pages)):
                writer.add_page(reader.pages[j])
            
            output_filename = f"{output_prefix}_part_{i // max_pages + 1}.pdf"
            with open(output_filename, 'wb') as output_file:
                writer.write(output_file)
            
            yield output_filename

def process_pdf(file_path):
    extracted_text = ""
    
    try:
        # Try to process the whole PDF
        with open(file_path, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-document", document=f, locale="ar-SA"
            )
        result = poller.result()
        
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"
    
    except HttpResponseError as e:
        if "InvalidContentLength" in str(e):
            print("PDF too large, splitting into smaller parts...")
            # Split the PDF and process each part
            for part_file in split_pdf(file_path, os.path.splitext(file_path)[0]):
                with open(part_file, "rb") as f:
                    poller = document_analysis_client.begin_analyze_document(
                        "prebuilt-document", document=f, locale="ar-SA"
                    )
                result = poller.result()
                
                for page in result.pages:
                    for line in page.lines:
                        extracted_text += line.content + "\n"
                
                os.remove(part_file)  # Remove the temporary split file
        else:
            raise e

    # Save to a local text file
    output_file = os.path.splitext(file_path)[0] + "_extracted.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    print(f"Extracted text saved to: {output_file}")

# Usage
pdf_file = r'C:\Users\abutair\workspace\gpt-poet\Kotobati.pdf'
process_pdf(pdf_file)