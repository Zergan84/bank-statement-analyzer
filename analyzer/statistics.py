from collections import defaultdict
from dataclasses import dataclass, field
from models.transaction import Transaction, TransactionCategory


@dataclass
class Statistics:
    total_count: int = 0
    total_income: float = 0.0
    total_expenses: float = 0.0
    balance: float = 0.0
    category_stats: dict[str, dict] = field(default_factory=lambda: defaultdict(lambda: {"count": 0, "total": 0.0}))
    unknown_count: int = 0
    unknown_transactions: list[Transaction] = field(default_factory=list)

    def compute(self, transactions: list[Transaction]) -> "Statistics":
        self.total_count = len(transactions)
        for tx in transactions:
            if tx.amount > 0:
                self.total_income += tx.amount
            else:
                self.total_expenses += abs(tx.amount)

            cat_name = tx.category.value if tx.category else "Unknown"
            self.category_stats[cat_name]["count"] += 1
            self.category_stats[cat_name]["total"] += tx.amount

            if tx.confidence_score < 0.6 or tx.category in (
                TransactionCategory.UNKNOWN_INCOME,
                TransactionCategory.UNKNOWN_EXPENSE,
            ):
                self.unknown_count += 1
                self.unknown_transactions.append(tx)

        self.balance = self.total_income - self.total_expenses
        return self
