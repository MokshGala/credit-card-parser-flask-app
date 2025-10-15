from flask import Flask, render_template, request, jsonify
import io
from parser import IndianCreditCardParser

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/parse', methods=['POST'])
def parse_statement():
    try:
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['pdf_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Please upload a PDF file'}), 400

        parser = IndianCreditCardParser()
        file_stream = io.BytesIO(file.read())
        statement_data = parser.parse_pdf_file(file_stream)

        if statement_data is None:
            return jsonify({'error': 'Failed to parse the PDF. Please ensure it is a valid credit card statement.'}), 400

        return jsonify(statement_data.to_dict())

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
