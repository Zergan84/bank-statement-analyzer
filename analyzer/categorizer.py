import logging
from models.transaction import Transaction, TransactionCategory
from .rules import apply_rules

logger = logging.getLogger(__name__)


class Categorizer:
    def categorize(self, transaction: Transaction) -> None:
        category, confidence = apply_rules(transaction)
        transaction.category = category
        transaction.confidence_score = confidence

    def categorize_batch(self, transactions: list[Transaction]) -> list[Transaction]:
        for tx in transactions:
            self.categorize(tx)
        return transactions
