from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Define API routes first to give them priority
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        loan_amount = float(data.get('loanAmount', 0))
        interest_rate = float(data.get('interestRate', 0))
        loan_term = float(data.get('loanTerm', 0))
        
        # Simple validation
        if loan_amount <= 0 or interest_rate <= 0 or loan_term <= 0:
            return jsonify({"error": "Please enter valid values for all fields"}), 400
            
        # Convert annual interest rate to monthly
        monthly_interest_rate = interest_rate / 12 / 100
        
        # Calculate total number of monthly payments
        total_payments = loan_term * 12
        
        # Calculate EMI (Equated Monthly Installment)
        emi = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments) / ((1 + monthly_interest_rate) ** total_payments - 1)
        
        # Calculate total payment over entire loan term
        total_payment = emi * total_payments
        
        # Calculate total interest paid
        total_interest = total_payment - loan_amount
        
        # Build comprehensive analysis
        analysis = {
            "emi": round(emi, 2),
            "totalPayment": round(total_payment, 2),
            "totalInterest": round(total_interest, 2),
            "loanAmount": loan_amount,
            "interestRate": interest_rate,
            "loanTerm": loan_term
        }
        
        formatted_response = f"""
        <h2>Loan Analysis Results</h2>
        <div style="margin-bottom: 20px;">
            <p><strong>Loan Amount:</strong> ₹{loan_amount:,.2f}</p>
            <p><strong>Interest Rate:</strong> {interest_rate:.2f}% per annum</p>
            <p><strong>Loan Term:</strong> {loan_term} years</p>
        </div>

        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: #1976d2;">Monthly Payment Details</h3>
            <p><strong>Monthly EMI:</strong> ₹{emi:,.2f}</p>
            <p><strong>Total Payment:</strong> ₹{total_payment:,.2f}</p>
            <p><strong>Total Interest:</strong> ₹{total_interest:,.2f}</p>
        </div>

        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #2e7d32;">Repayment Insights</h3>
            <p>Your loan will be fully repaid after {total_payments} monthly payments.</p>
            <p>The interest component represents {(total_interest/total_payment)*100:.1f}% of your total payments.</p>
            <p>You'll pay ₹{total_interest/loan_amount*100:.1f}% of your principal amount as interest over the loan term.</p>
        </div>
        """
        
        return jsonify({"response": formatted_response, "analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '')
        
        # Simple AI response logic
        if not question:
            return jsonify({"error": "Please provide a question"}), 400
        
        # Basic response patterns
        response = ""
        lower_question = question.lower()
        
        # Check for different question types
        if any(word in lower_question for word in ['emi', 'equated', 'monthly', 'installment']):
            response = """EMI (Equated Monthly Installment) is the fixed payment amount you make each month to repay your loan.
            
It is calculated using the formula: EMI = P × r × (1 + r)^n / ((1 + r)^n - 1), where:
- P is the loan principal amount
- r is the monthly interest rate (annual rate ÷ 12 ÷ 100)
- n is the total number of monthly payments (loan term in years × 12)

A higher loan amount or interest rate increases your EMI, while a longer loan term reduces it but increases the total interest paid."""
            
        elif any(word in lower_question for word in ['interest', 'rate']):
            response = """Interest rate determines how much you pay for borrowing money, expressed as an annual percentage.
            
For home loans in India, rates typically range from 6.5% to 9.5% depending on the lender, your credit score, loan amount, and term. Personal loan rates are usually higher, ranging from 10.5% to 18%.

Different types of interest rates include:
1. Fixed rate: Remains the same throughout the loan term
2. Floating rate: Can change based on market conditions
3. Repo rate linked: Directly tied to RBI's repo rate changes

A lower interest rate can save you significant money over the life of the loan."""
            
        elif any(word in lower_question for word in ['prepay', 'prepayment', 'early']):
            response = """Prepayment means paying more than your scheduled EMI or making a lump sum payment toward your loan principal.
            
Benefits of prepayment:
- Reduces the outstanding principal
- Decreases the total interest paid
- Shortens your loan term

Most banks in India allow prepayment on home loans without penalties, but personal loans may have prepayment charges of 2-5% of the prepaid amount.

For maximum benefit, consider making prepayments early in your loan term when the interest component is highest."""
            
        elif any(word in lower_question for word in ['credit', 'score', 'cibil']):
            response = """Your credit score (commonly CIBIL score in India) ranges from 300-900 and significantly impacts your loan eligibility and interest rates.
            
Score ranges and their implications:
- 750-900: Excellent - Best loan terms and lowest interest rates
- 700-749: Good - Favorable loan terms
- 650-699: Fair - May qualify for standard rates
- Below 650: Poor - Difficulty obtaining loans or higher rates

Factors affecting your credit score:
1. Payment history (35%)
2. Credit utilization (30%)
3. Length of credit history (15%)
4. Types of credit (10%)
5. Recent credit inquiries (10%)

Maintain a good score by paying bills on time and keeping credit card balances low."""
            
        elif any(word in lower_question for word in ['term', 'tenure', 'duration']):
            response = """Loan term (or tenure) is the time period over which you repay your loan.
            
Common loan terms in India:
- Home loans: 5-30 years
- Personal loans: 1-5 years
- Car loans: 1-7 years
- Education loans: 5-15 years

A longer loan term means:
- Lower monthly EMI payments
- Higher total interest paid
- More time to repay the loan

A shorter loan term means:
- Higher monthly EMI payments
- Lower total interest paid
- Faster debt freedom

Choose a loan term that balances affordable monthly payments with minimizing interest costs."""
            
        elif any(word in lower_question for word in ['compare', 'difference', 'versus', 'vs']):
            response = """When comparing loan offers, look beyond just the interest rate. Consider:

1. Total cost of the loan (interest + all fees)
2. Type of interest rate (fixed vs. floating)
3. Processing fees (usually 0.5-2% of loan amount)
4. Prepayment penalties and conditions
5. Foreclosure charges
6. Insurance requirements
7. Customer service quality
8. Disbursal time

For home loans, public sector banks like SBI often offer lower rates but may have slower processing. Private banks like HDFC or ICICI might have slightly higher rates but faster approval and better service.

Always calculate the total cost over the entire loan term rather than focusing only on the monthly EMI."""
            
        else:
            response = """I can help you with various loan and finance related queries, such as:

- EMI calculations and formulas
- Interest rates and types
- Loan terms and their impact
- Prepayment strategies
- Credit score improvement
- Comparing loan offers
- Tax benefits on loans
- Home loan, personal loan, or car loan specifics

Please ask me a specific question about your financial needs or loan concerns."""
        
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Define static file routes after API routes
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/app.html')
def app_html():
    return send_from_directory('.', 'app.html')

@app.route('/result.html')
def result_html():
    return send_from_directory('.', 'result.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True) 