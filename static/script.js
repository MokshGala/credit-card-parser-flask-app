document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const errorMessage = document.getElementById('errorMessage');

    loading.style.display = 'block';
    results.style.display = 'none';
    errorMessage.style.display = 'none';

    try {
        const response = await fetch('/parse', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        loading.style.display = 'none';

        if (data.error) {
            errorMessage.textContent = data.error;
            errorMessage.style.display = 'block';
        } else {
            displayResults(data);
            results.style.display = 'block';
        }
    } catch (error) {
        loading.style.display = 'none';
        errorMessage.textContent = 'Error: ' + error.message;
        errorMessage.style.display = 'block';
    }
});

function displayResults(data) {
    const results = document.getElementById('results');
    let transactionsHTML = '';

    data.transactions.forEach(txn => {
        const typeClass = txn.transaction_type === 'credit' ? 'transaction-credit' : 'transaction-debit';
        transactionsHTML += `
            <tr>
                <td>${txn.date}</td>
                <td>${txn.description}</td>
                <td class="${typeClass}">₹${txn.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                <td>${txn.transaction_type.toUpperCase()}</td>
            </tr>
        `;
    });

    results.innerHTML = `
        <h2 class="section-title">📊 Statement Summary</h2>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="bank-badge">${data.issuer}</div>
                <div class="summary-label">Card Number</div>
                <div class="summary-value">**** ${data.card_last_four}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Statement Period</div>
                <div class="summary-value" style="font-size:1.1em;">${data.statement_period}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Payment Due Date</div>
                <div class="summary-value">${data.payment_due_date}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Total Amount Due</div>
                <div class="summary-value">₹${data.total_amount_due.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Minimum Amount Due</div>
                <div class="summary-value">₹${data.minimum_amount_due.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
            </div>
        </div>

        <h2 class="section-title">💰 Transactions</h2>
        <div style="margin-bottom: 15px; color:#a0a0ff;">Total Transactions: ${data.transactions.length}</div>
        <div style="overflow-x:auto;">
            <table class="transactions-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
                    ${transactionsHTML}
                </tbody>
            </table>
        </div>

        <div style="text-align:center; margin-top:30px;">
            <button class="btn" onclick="location.reload()">Parse Another Statement</button>
        </div>
    `;
}
