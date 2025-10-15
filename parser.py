import re
from typing import Optional, List
import PyPDF2
from models import StatementData, Transaction


class IndianCreditCardParser:
    ISSUER_PATTERNS = {
        'HDFC Bank': r'hdfc\s*bank|hdfc\s*credit\s*card',
        'ICICI Bank': r'icici\s*bank|icici\s*credit\s*card',
        'SBI Card': r'sbi\s*card|state bank|sbi\s*credit',
        'Axis Bank': r'axis\s*bank|axis\s*credit\s*card',
        'Kotak Mahindra': r'kotak|kotak\s*mahindra',
    }

    def __init__(self):
        self.text = ""
        self.issuer = "Unknown"

    def parse_pdf_file(self, file_stream) -> Optional[StatementData]:
        try:
            self.text = self._extract_text_from_pdf_stream(file_stream)
            self.issuer = self._identify_issuer()

            card_last_four = self._extract_card_last_four()
            statement_period = self._extract_statement_period()
            payment_due_date = self._extract_payment_due_date()
            total_amount_due = self._extract_total_amount_due()
            minimum_amount_due = self._extract_minimum_amount_due()
            transactions = self._extract_transactions()

            return StatementData(
                issuer=self.issuer,
                card_last_four=card_last_four,
                statement_period=statement_period,
                payment_due_date=payment_due_date,
                total_amount_due=total_amount_due,
                minimum_amount_due=minimum_amount_due,
                transactions=transactions
            )
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return None

    def _extract_text_from_pdf_stream(self, file_stream) -> str:
        text = ""
        pdf_reader = PyPDF2.PdfReader(file_stream)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    def _identify_issuer(self) -> str:
        text_lower = self.text.lower()
        for issuer, pattern in self.ISSUER_PATTERNS.items():
            if re.search(pattern, text_lower):
                return issuer
        return "Unknown"

    def _extract_card_last_four(self) -> str:
        patterns = [
            r'card\s*number[:\s]+[xX*]+\s*(\d{4})',
            r'card\s*ending\s*(?:in|with)[:\s]*(\d{4})',
            r'xxxx\s*xxxx\s*xxxx\s*(\d{4})',
            r'[xX*]{4}[\s\-]?[xX*]{4}[\s\-]?[xX*]{4}[\s\-]?(\d{4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1)
        return "****"

    def _extract_statement_period(self) -> str:
        patterns = [
            r'statement\s*period[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|-)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'billing\s*period[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|-)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'from\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+to\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return f"{match.group(1)} to {match.group(2)}"
        return "Not found"

    def _extract_payment_due_date(self) -> str:
        patterns = [
            r'payment\s*due\s*date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'due\s*date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'pay\s*by[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "Not found"

    def _extract_total_amount_due(self) -> float:
        patterns = [
            r'total\s*amount\s*due[:\s]+(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'total\s*due[:\s]+(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'amount\s*due[:\s]+(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'outstanding\s*balance[:\s]+(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'closing\s*balance[:\s]+(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return 0.0

    def _extract_minimum_amount_due(self) -> float:
        patterns = [
            r'minimum\s*amount\s*due[:\s]+(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'minimum\s*due[:\s]+(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'min\.?\s*amount\s*due[:\s]+(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return 0.0

    def _extract_transactions(self) -> List[Transaction]:
        transactions = []
        pattern = r'(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\s+([A-Za-z0-9\s\.\-\'&@*\/,]+?)\s+(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)\s*(?:Dr|Cr)?'
        matches = re.finditer(pattern, self.text, re.IGNORECASE | re.MULTILINE)

        for match in matches:
            date = match.group(1)
            description = match.group(2).strip()
            amount_str = match.group(3).replace(',', '')

            try:
                amount = float(amount_str)
            except ValueError:
                continue

            transaction_type = 'debit'
            if re.search(r'\bCr\b', match.group(0), re.IGNORECASE) or any(k in description.lower() for k in ['payment', 'credit', 'reversal', 'refund']):
                transaction_type = 'credit'

            if (len(description) > 3 and
                amount > 0 and
                not any(keyword in description.lower() for keyword in ['total', 'balance', 'summary', 'page', 'statement'])):
                transactions.append(Transaction(
                    date=date,
                    description=description[:60],
                    amount=amount,
                    transaction_type=transaction_type
                ))

        seen = set()
        unique_transactions = []
        for txn in transactions:
            txn_key = (txn.date, txn.description, txn.amount)
            if txn_key not in seen:
                seen.add(txn_key)
                unique_transactions.append(txn)

        return unique_transactions[:50]
