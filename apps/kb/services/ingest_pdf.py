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


def extract_text_ocr_fallback(pdf_path: Path, page_num: int, dpi: int = 150) -> str:
    """Targeted OCR fallback using PyMuPDF for rendering an individual page."""
    try:
        with fitz.open(pdf_path) as doc:
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
            print(
                f"Failed to extract text using mode {mode} on page {page_num}, Error: {e}"
            )

    return ""


def process_single_pdf(pdf_path: Path) -> list[Document]:
    """Processes a single PDF file and extracts content from all its pages."""
    pdf_documents = []
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    print(f"📖 Processing '{pdf_path.name}' ({total_pages} pages)...")

    for page_num, page in enumerate(reader.pages):
        try:
            # 1. Digital Text Cascade (Plain -> Layout -> Standard)
            text = safe_extract(page, page_num + 1)

            # 2. OCR Fallback Cascade
            is_ocr_used = False
            if not text:
                text = extract_text_ocr_fallback(pdf_path, page_num)
                is_ocr_used = True

            # 3. Commit Document block if any text was rescued
            if text and text.strip():
                pdf_documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": str(pdf_path),
                            "file_name": pdf_path.name,
                            "page": page_num + 1,
                            "total_pages": total_pages,
                            "extraction_method": "ocr" if is_ocr_used else "digital",
                        },
                    )
                )
        except Exception as e:
            print(f"⚠️ Failed page {page_num + 1} " f"of {pdf_path.name}: {e}")

    # Warn if the entire file resulted in absolute emptiness
    if not pdf_documents:
        print(
            f"  ⚠️ Warning: Successfully read '{pdf_path.name}' but 0 characters were extracted across all pages."
        )

    return pdf_documents


def ingest_pdf_directory(directory_path: str) -> list[Document]:
    """
    Main entrypoint. Pass a directory path, scan recursively,
    and receive a flat list of parsed Document objects.
    """
    all_documents = []
    path = Path(directory_path)

    success_count = 0
    error_count = 0

    # Ensure target directory actually exists
    if not path.is_dir():
        print(f"❌ Error: Provided path is not a valid directory: {directory_path}")
        return []

    for pdf_path in path.glob("**/*.pdf"):
        try:
            # Process individual file via isolated worker function
            file_docs = process_single_pdf(pdf_path)
            all_documents.extend(file_docs)
            success_count += 1
            print(f"✅processed: {pdf_path.name}  🟢total_pages: {len(file_docs)}")
        except Exception as e:
            error_count += 1
            print(f"❌ Critical error parsing file {pdf_path.name}: {e}")

    print(
        f"\n--- Ingestion Summary: Successfully parsed {success_count} PDFs. Failed on {error_count} PDFs. ---"
    )
    return all_documents
