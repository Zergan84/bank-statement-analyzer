from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TransactionType(str, Enum):
    INCOME = "Income"
    EXPENSE = "Expense"
    UNKNOWN = "Unknown"


class TransactionCategory(str, Enum):
    SALARY = "Salary"
    BUSINESS_INCOME = "Business income"
    CLIENT_PAYMENT = "Client payment"
    REFUND = "Refund"
    LOAN_REPAYMENT = "Loan repayment"
    GIFT = "Gift"
    TRANSFER = "Transfer"
    RENT = "Rent"
    FOOD = "Food"
    TRANSPORT = "Transport"
    INSURANCE = "Insurance"
    TAXES = "Taxes"
    BANK_FEES = "Bank fees"
    SUBSCRIPTION = "Subscription"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    HEALTH = "Health"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    EDUCATION = "Education"
    UNKNOWN_INCOME = "Unknown income"
    UNKNOWN_EXPENSE = "Unknown expense"


@dataclass
class Transaction:
    date: datetime
    description: str
    amount: float
    currency: str = "EUR"
    type: TransactionType = TransactionType.UNKNOWN
    category: TransactionCategory = TransactionCategory.UNKNOWN_INCOME
    sender: str = ""
    recipient: str = ""
    reference: str = ""
    confidence_score: float = 0.0
    comment: str = ""
    id: str = field(default_factory=lambda: "")

    def __post_init__(self) -> None:
        if self.amount > 0:
            self.type = TransactionType.INCOME
        elif self.amount < 0:
            self.type = TransactionType.EXPENSE
        else:
            self.type = TransactionType.UNKNOWN
