import logging
import re
from datetime import datetime
from typing import Optional

import pdfplumber

from models.transaction import Transaction

logger = logging.getLogger(__name__)

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


class PDFExtractor:
    def extract(self, pdf_path: str) -> list[Transaction]:
        raise NotImplementedError


class RevolutExtractor(PDFExtractor):
    """Parser for Revolut PDF statements."""

    def extract(self, pdf_path: str) -> list[Transaction]:
        transactions: list[Transaction] = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        transactions.extend(self._parse_page(text))
        except Exception:
            logger.exception("Failed to extract text from PDF")
            raise
        return transactions

    def _parse_page(self, text: str) -> list[Transaction]:
        transactions: list[Transaction] = []
        lines = text.strip().split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            tx_date = self._parse_date_from_line(line)
            if tx_date is None:
                i += 1
                continue

            amount, balance = self._extract_amounts(line)
            if amount is None:
                i += 1
                continue

            description = self._extract_description(line)

            details_lines: list[str] = []
            j = i + 1
            while j < len(lines) and self._parse_date_from_line(lines[j]) is None:
                details_lines.append(lines[j])
                j += 1

            combined_details = " ".join(details_lines)
            recipient = self._extract_recipient(combined_details)
            reference = self._extract_reference(combined_details)
            has_from = "From:" in combined_details
            has_to = "To:" in combined_details

            if has_to and not has_from:
                signed_amount = -abs(amount)
            elif has_from and not has_to:
                signed_amount = abs(amount)
            else:
                desc_lower = description.lower()
                if any(kw in desc_lower for kw in
                       ["deposit", "top-up", "refund", "transfer from", "from:", "cashback",
                        "salary", "income", "payment from", "received"]):
                    signed_amount = abs(amount)
                elif any(kw in desc_lower for kw in
                         ["transfer to", "to:", "payment to", "withdrawal"]):
                    signed_amount = -abs(amount)
                else:
                    signed_amount = -abs(amount)

            tx = Transaction(
                date=tx_date,
                description=description,
                amount=signed_amount,
                currency="EUR",
                recipient=recipient,
                reference=reference,
            )
            transactions.append(tx)

            i = j
        return transactions

    def _parse_date_from_line(self, line: str) -> Optional[datetime]:
        pattern = r"([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})"
        m = re.search(pattern, line)
        if not m:
            return None
        return self._parse_date_str(m.group(1))

    def _parse_date_str(self, date_str: str) -> Optional[datetime]:
        try:
            parts = date_str.replace(",", "").split()
            if len(parts) == 3:
                month = MONTHS.get(parts[0].strip().lower()[:3])
                day = int(parts[1])
                year = int(parts[2])
                if month:
                    return datetime(year, month, day)
        except (ValueError, IndexError):
            pass
        return None

    def _extract_amounts(self, line: str) -> tuple[Optional[float], Optional[float]]:
        amounts = re.findall(r"€([0-9]+(?:[.,][0-9]+)*)", line)
        if not amounts:
            return None, None
        parsed = []
        for a in amounts:
            a_clean = a.replace(",", "")
            try:
                parsed.append(float(a_clean))
            except ValueError:
                parsed.append(None)
        if len(parsed) >= 1 and parsed[0] is not None:
            balance = parsed[-1] if len(parsed) >= 2 and parsed[-1] is not None else None
            return parsed[0], balance
        return None, None

    def _extract_description(self, line: str) -> str:
        date_pattern = r"[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}"
        all_dates = re.findall(date_pattern, line)
        rest = line
        for d in all_dates:
            rest = rest.replace(d, "", 1)

        idx = rest.find("€")
        if idx != -1:
            rest = rest[:idx]
        return rest.strip().strip("-").strip()

    def _extract_recipient(self, details: str) -> str:
        m = re.search(r"(?:To:|From:)\s*(.*?)(?:\s+Card:|\s+Reference:|$)", details)
        if m:
            return m.group(1).strip()
        return ""

    def _extract_reference(self, details: str) -> str:
        m = re.search(r"Reference:\s*(.*?)(?:\s+To:|\s+From:|\s+Card:|$)", details)
        if m:
            return m.group(1).strip()
        return ""


class SimpleTextExtractor(PDFExtractor):
    def extract(self, pdf_path: str) -> list[Transaction]:
        transactions: list[Transaction] = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        transactions.extend(self._parse_text(text))
        except Exception:
            logger.exception("Failed to extract text from PDF")
            raise
        return transactions

    def _parse_text(self, text: str) -> list[Transaction]:
        transactions: list[Transaction] = []
        lines = text.strip().split("\n")
        for i, line in enumerate(lines):
            tx = self._try_parse_line(line)
            if tx:
                transactions.append(tx)
        return transactions

    def _try_parse_line(self, line: str) -> Optional[Transaction]:
        date_pattern = re.compile(
            r"(\d{2}[./-]\d{2}[./-]\d{2,4})"
        )
        amount_pattern = re.compile(
            r"([+-]?\s?\d{1,3}(?:\s?\d{3})*(?:[.,]\d{2})?)"
        )
        date_match = date_pattern.search(line)
        if not date_match:
            return None

        date_str = date_match.group(1)
        date = self._parse_date(date_str)
        if date is None:
            return None

        amount_match = amount_pattern.search(line, date_match.end())
        if not amount_match:
            return None

        amount_str = amount_match.group(1).replace(" ", "").replace(",", ".")
        try:
            amount = float(amount_str)
        except ValueError:
            return None

        description = line[date_match.end() : amount_match.start()].strip()
        if not description:
            description = line.strip()

        return Transaction(
            date=date,
            description=description,
            amount=amount,
        )

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        separators = [".", "/", "-"]
        for sep in separators:
            if sep in date_str:
                parts = date_str.split(sep)
                if len(parts) == 3:
                    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                    if year < 100:
                        year += 2000
                    try:
                        return datetime(year, month, day)
                    except ValueError:
                        return None
        return None


class TableExtractor(PDFExtractor):
    def extract(self, pdf_path: str) -> list[Transaction]:
        transactions: list[Transaction] = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            tx = self._parse_row(row)
                            if tx:
                                transactions.append(tx)
        except Exception:
            logger.exception("Failed to extract tables from PDF")
            raise
        return transactions

    def _parse_row(self, row: list[Optional[str]]) -> Optional[Transaction]:
        cleaned = [str(cell).strip() if cell else "" for cell in row]
        if not any(cleaned):
            return None

        full_text = " ".join(cleaned)

        date_pattern = re.compile(r"(\d{2}[./-]\d{2}[./-]\d{2,4})")
        amount_pattern = re.compile(r"([+-]?\s?\d{1,3}(?:\s?\d{3})*(?:[.,]\d{2})?)")

        date_match = date_pattern.search(full_text)
        if not date_match:
            return None
        date_str = date_match.group(1)

        separators = [".", "/", "-"]
        date_obj = None
        for sep in separators:
            if sep in date_str:
                parts = date_str.split(sep)
                if len(parts) == 3:
                    d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                    if y < 100:
                        y += 2000
                    try:
                        date_obj = datetime(y, m, d)
                    except ValueError:
                        pass
                    break
        if date_obj is None:
            return None

        amount_matches = amount_pattern.findall(full_text[date_match.end() :])
        if not amount_matches:
            return None

        amount_str = amount_matches[-1].replace(" ", "").replace(",", ".")
        try:
            amount = float(amount_str)
        except ValueError:
            return None

        desc_parts = []
        for cell in cleaned:
            cell_clean = cell.strip()
            if cell_clean and not date_pattern.match(cell_clean) and not amount_pattern.match(cell_clean):
                desc_parts.append(cell_clean)

        description = " ".join(desc_parts) if desc_parts else full_text

        return Transaction(
            date=date_obj,
            description=description,
            amount=amount,
        )
