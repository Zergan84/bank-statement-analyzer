import logging
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

from pdf_parser.extractor import PDFExtractor, RevolutExtractor
from analyzer.categorizer import Categorizer
from analyzer.statistics import Statistics
from exporter.excel_generator import ExcelGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class BankAnalyzerApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Bank Statement Analyzer")
        self.setMinimumSize(640, 500)

        self.pdf_path: str = ""
        self.transactions: list = []
        self.stats: Statistics = Statistics()

        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QLabel("Bank Statement Analyzer")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            "background-color: #1F4E79; color: white; padding: 14px; font-size: 18px; font-weight: bold;"
        )
        layout.addWidget(header)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 12, 20, 20)
        layout.addWidget(body)

        select_row = QHBoxLayout()
        self.select_btn = QPushButton("Select PDF")
        self.select_btn.setStyleSheet(
            "QPushButton { background-color: #1F4E79; color: white; padding: 8px 24px; font-size: 11pt; border-radius: 4px; }"
            "QPushButton:hover { background-color: #2a5f9e; }"
        )
        self.select_btn.clicked.connect(self._select_pdf)
        select_row.addWidget(self.select_btn)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #666; font-size: 10pt; padding-left: 8px;")
        select_row.addWidget(self.file_label)
        select_row.addStretch()
        body_layout.addLayout(select_row)

        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setStyleSheet(
            "QPushButton { background-color: #00B050; color: white; padding: 8px 24px; font-size: 11pt; border-radius: 4px; }"
            "QPushButton:hover { background-color: #00c853; }"
            "QPushButton:disabled { background-color: #ccc; }"
        )
        self.analyze_btn.clicked.connect(self._analyze)
        body_layout.addWidget(self.analyze_btn)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Courier", 10))
        self.result_text.setStyleSheet(
            "QTextEdit { background-color: white; border: 1px solid #ddd; padding: 8px; }"
        )
        body_layout.addWidget(self.result_text, stretch=1)

        self.export_btn = QPushButton("Export XLSX")
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet(
            "QPushButton { background-color: #1F4E79; color: white; padding: 8px 24px; font-size: 11pt; border-radius: 4px; }"
            "QPushButton:hover { background-color: #2a5f9e; }"
            "QPushButton:disabled { background-color: #ccc; }"
        )
        self.export_btn.clicked.connect(self._export)
        body_layout.addWidget(self.export_btn)

    def _select_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Bank Statement PDF", "", "PDF files (*.pdf);;All files (*.*)"
        )
        if path:
            self.pdf_path = path
            self.file_label.setText(os.path.basename(path))
            self.analyze_btn.setEnabled(True)
            self.result_text.setText(f"Selected: {os.path.basename(path)}\nReady to analyze.\n")

    def _analyze(self) -> None:
        if not self.pdf_path:
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return

        self.result_text.setText("Analyzing...\n")
        QApplication.processEvents()

        try:
            extractor = self._get_extractor()
            self.transactions = extractor.extract(self.pdf_path)

            if not self.transactions:
                self.result_text.setText(
                    "No transactions found.\nTry a different extraction method.\n"
                )
                self.export_btn.setEnabled(False)
                return

            categorizer = Categorizer()
            categorizer.categorize_batch(self.transactions)

            self.stats = Statistics().compute(self.transactions)

            self._show_result()
            self.export_btn.setEnabled(True)

        except Exception as e:
            logger.exception("Analysis failed")
            self.result_text.setText(f"\nError: {e}\n")
            QMessageBox.critical(self, "Error", f"Analysis failed:\n{e}")

    def _get_extractor(self) -> PDFExtractor:
        return RevolutExtractor()

    def _show_result(self) -> None:
        currency = self.transactions[0].currency if self.transactions else "EUR"
        report = (
            f"Analysis complete!\n"
            f"{'─' * 40}\n"
            f"  Transactions:    {self.stats.total_count}\n"
            f"  Income:          +{self.stats.total_income:,.2f} {currency}\n"
            f"  Expenses:        -{self.stats.total_expenses:,.2f} {currency}\n"
            f"  Balance:         {self.stats.balance:+,.2f} {currency}\n"
            f"  Unknown:         {self.stats.unknown_count}\n"
            f"  Categories:      {len(self.stats.category_stats)}\n"
            f"{'─' * 40}\n"
        )
        self.result_text.setText(report)

    def _export(self) -> None:
        if not self.transactions:
            QMessageBox.warning(self, "Warning", "Nothing to export.")
            return

        default_name = f"Bank_analysis_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel Report", default_name, "Excel files (*.xlsx)"
        )
        if not path:
            return

        try:
            gen = ExcelGenerator(
                self.transactions,
                self.stats,
                source_pdf=os.path.basename(self.pdf_path),
            )
            gen.generate(path)
            QMessageBox.information(self, "Success", f"Report saved:\n{path}")
            self.result_text.append(f"\nExported: {os.path.basename(path)}\n")
        except Exception as e:
            logger.exception("Export failed")
            QMessageBox.critical(self, "Error", f"Export failed:\n{e}")


def main() -> None:
    import sys
    app = QApplication(sys.argv)
    window = BankAnalyzerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
