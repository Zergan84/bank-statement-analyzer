import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OCRProcessor:
    def process(self, pdf_path: str) -> Optional[str]:
        try:
            import pytesseract
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path)
            text_parts: list[str] = []
            for image in images:
                text = pytesseract.image_to_string(image, lang="eng+rus")
                text_parts.append(text)
            return "\n".join(text_parts)
        except ImportError:
            logger.warning(
                "pytesseract or pdf2image not installed. "
                "Install: pip install pytesseract pdf2image"
            )
            return None
        except Exception:
            logger.exception("OCR processing failed")
            return None
