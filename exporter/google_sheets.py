import logging
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class GoogleSheetsExporter:
    def __init__(self) -> None:
        self._service = None

    def _get_service(self):
        if self._service is not None:
            return self._service
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError:
            raise RuntimeError(
                "Install google-api-python-client: pip install google-api-python-client google-auth"
            )

        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not creds_json:
            raise RuntimeError(
                "GOOGLE_SERVICE_ACCOUNT_JSON env var not set. "
                "Create a service account in Google Cloud Console, "
                "enable Google Sheets API, and set this env var to the JSON key."
            )

        try:
            creds_info = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_info,
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
            self._service = build("sheets", "v4", credentials=creds)
            return self._service
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google Sheets client: {e}")

    def export(self, transactions, stats, source_pdf: str) -> str:
        service = self._get_service()

        spreadsheet = {
            "properties": {
                "title": f"Bank Analysis {datetime.now().strftime('%Y-%m-%d')}",
            },
            "sheets": [
                {"properties": {"title": "Transactions"}},
                {"properties": {"title": "Summary"}},
                {"properties": {"title": "Categories"}},
                {"properties": {"title": "Unknown"}},
            ],
        }

        sheet = service.spreadsheets().create(body=spreadsheet).execute()
        sheet_id = sheet["spreadsheetId"]
        url = sheet["spreadsheetUrl"]

        self._write_transactions(service, sheet_id, transactions)
        self._write_summary(service, sheet_id, stats, source_pdf)
        self._write_categories(service, sheet_id, stats)
        self._write_unknown(service, sheet_id, stats)

        logger.info("Google Sheet created: %s", url)
        return url

    def _write_transactions(self, service, sheet_id, transactions):
        headers = [
            "Date", "Type", "Sender/Recipient", "Description",
            "Amount", "Currency", "Category", "Confidence",
        ]
        rows = [headers]
        for tx in transactions:
            rows.append([
                tx.date.strftime("%d.%m.%Y") if tx.date else "",
                tx.type.value if tx.type else "",
                tx.sender or tx.recipient or "",
                tx.description,
                tx.amount,
                tx.currency,
                tx.category.value if tx.category else "",
                tx.confidence_score,
            ])

        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="Transactions!A1",
            valueInputOption="USER_ENTERED",
            body={"values": rows},
        ).execute()

    def _write_summary(self, service, sheet_id, stats, source_pdf):
        rows = [
            ["SUMMARY"],
            [f"Source: {source_pdf}"],
            [],
            ["Total transactions:", stats.total_count],
            ["Total Income:", round(stats.total_income, 2)],
            ["Total Expenses:", round(stats.total_expenses, 2)],
            ["Balance:", round(stats.balance, 2)],
            ["Categories used:", len(stats.category_stats)],
        ]

        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="Summary!A1",
            valueInputOption="USER_ENTERED",
            body={"values": rows},
        ).execute()

    def _write_categories(self, service, sheet_id, stats):
        rows = [["Category", "Count", "Total"]]
        for cat_name, data in sorted(stats.category_stats.items(), key=lambda x: -abs(x[1]["total"])):
            rows.append([cat_name, data["count"], round(data["total"], 2)])

        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="Categories!A1",
            valueInputOption="USER_ENTERED",
            body={"values": rows},
        ).execute()

    def _write_unknown(self, service, sheet_id, stats):
        rows = [["Date", "Description", "Amount", "Currency", "Category", "Confidence"]]
        for tx in stats.unknown_transactions:
            rows.append([
                tx.date.strftime("%d.%m.%Y") if tx.date else "",
                tx.description,
                tx.amount,
                tx.currency,
                tx.category.value if tx.category else "",
                tx.confidence_score,
            ])

        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="Unknown!A1",
            valueInputOption="USER_ENTERED",
            body={"values": rows},
        ).execute()
