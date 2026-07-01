from pypdf import PdfReader
from pathlib import Path
import fitz
from PIL import Image
import pytesseract
import io


class Document:
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata


def extract_text_ocr_fallback(pdf_source, page_num: int, dpi: int = 150) -> str:
    """Targeted OCR fallback handling both file paths and in-memory bytes."""
    try:
        # If it's a Django file stream or raw bytes, load it via stream memory
        if isinstance(pdf_source, (bytes, bytearray)):
            doc = fitz.open(stream=pdf_source, filetype="pdf")
        elif hasattr(pdf_source, 'read'):
            pdf_source.seek(0)
            doc = fitz.open(stream=pdf_source.read(), filetype="pdf")
        else:
            doc = fitz.open(pdf_source)

        with doc:
            page = doc[page_num]
            pix = page.get_pixmap(dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            return pytesseract.image_to_string(img, config="--psm 6").strip()
    except Exception as ocr_err:
        print(f"  ⚠️ OCR fallback failed on page {page_num + 1}: {ocr_err}")
        return ""


def safe_extract(page, page_num: int) -> str:
    for mode in ["plain", "layout", None]:
        try:
            if mode:
                text = page.extract_text(extraction_mode=mode)
            else:
                text = page.extract_text()
            if text and text.strip():
                return text
        except Exception as e:
            print(f"Failed to extract text using mode {mode} on page {page_num}, Error: {e}")
    return ""


def process_single_pdf(pdf_source, file_name: str) -> list[Document]:
    """
    Core Extraction Engine.
    pdf_source can be a Path object or a Django UploadedFile memory pointer.
    """
    pdf_documents = []

    # 📍 Step A: Ensure memory streams are at byte position zero
    if hasattr(pdf_source, 'seek'):
        pdf_source.seek(0)

    # 📍 Step B: Initialize reader (pypdf natively accepts paths or file-like streams!)
    reader = PdfReader(pdf_source)
    total_pages = len(reader.pages)

    print(f"📖 Extraction Engine Processing: '{file_name}' ({total_pages} pages)...")

    # Save an immutable reference to the raw file data for OCR fallbacks if needed
    ocr_source = pdf_source
    if hasattr(pdf_source, 'read'):
        pdf_source.seek(0)
        ocr_source = pdf_source.read()

    for page_num, page in enumerate(reader.pages):
        try:
            # 1. Digital Text Cascade (Plain -> Layout -> Standard)
            text = safe_extract(page, page_num + 1)

            # 2. OCR Fallback Cascade (Fires if text is completely empty)
            is_ocr_used = False
            if not text:
                text = extract_text_ocr_fallback(ocr_source, page_num)
                is_ocr_used = True

            # 3. Commit block
            if text and text.strip():
                pdf_documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": file_name,
                            "file_name": file_name,
                            "page": page_num + 1,
                            "total_pages": total_pages,
                            "extraction_method": "ocr" if is_ocr_used else "digital",
                        },
                    )
                )
        except Exception as e:
            print(f"⚠️ Failed page {page_num + 1} of {file_name}: {e}")

    return pdf_documents


def ingest_pdf_directory(directory_path: str) -> list[Document]:
    """Scans local directories on disk, wrapping the main engine function."""
    all_documents = []
    path = Path(directory_path)

    if not path.is_dir():
        print(f"❌ Error: Invalid directory: {directory_path}")
        return []

    for pdf_path in path.glob("**/*.pdf"):
        try:
            file_docs = process_single_pdf(pdf_path, pdf_path.name)
            all_documents.extend(file_docs)
        except Exception as e:
            print(f"❌ Error parsing {pdf_path.name}: {e}")

    return all_documents