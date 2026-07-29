import logging

logger = logging.getLogger(__name__)


class CamelotParser:
    def parse(self, pdf_path: str) -> list[list[str]]:
        rows: list[list[str]] = []
        try:
            import camelot
            tables = camelot.read_pdf(pdf_path, pages="all")
            for table in tables:
                for row in table.data:
                    rows.append(row)
        except ImportError:
            logger.warning("camelot not installed, skipping table parsing")
        except Exception:
            logger.exception("camelot parsing failed")
        return rows
