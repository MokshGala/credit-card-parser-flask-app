from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class Transaction:
    date: str
    description: str
    amount: float
    transaction_type: str


@dataclass
class StatementData:
    issuer: str
    card_last_four: str
    statement_period: str
    payment_due_date: str
    total_amount_due: float
    minimum_amount_due: float
    transactions: List[Transaction]

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['transactions'] = [asdict(t) for t in self.transactions]
        return data
