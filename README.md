# 💳 Credit Card Parser - Flask Web App

![Python](https://img.shields.io/badge/python-3.11-blue)
![Flask](https://img.shields.io/badge/flask-2.3-blueviolet)

A modern web application built with **Flask** to parse Indian credit card statements (HDFC, ICICI, SBI, Axis, Kotak). Features a futuristic dark-blue themed UI.

## Features
- Upload PDF statements
- Extract card info, total due, minimum due, payment dates
- Extract last 50 transactions (credit/debit)
- Modern dark-futuristic UI

## Tech Stack
- Python, Flask, PyPDF2
- HTML, CSS (futuristic theme), JavaScript

## Setup
```bash
git clone https://github.com/<username>/<repo-name>.git
cd <repo-name>
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

