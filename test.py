from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
import google.generativeai as genai
import os
import math

app = Flask(__name__)
CORS(app)

# Set your Gemini API key here
genai.configure(api_key="AIzaSyChir6dDtChsWFSRaVl3AjBSPKUvlKdnDA")

model = genai.GenerativeModel("gemini-2.0-flash")

def calculate_simple_interest(principal, rate, time):
    interest = (principal * rate * time) / 100
    total_amount = principal + interest
    return interest, total_amount

def calculate_compound_interest(principal, rate, time):
    n = 1  # Compounded annually
    amount = principal * (pow((1 + rate / (n * 100)), n * time))
    interest = amount - principal
    return interest, amount

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    try:
        loan_amount = float(data['loanAmount'])
        interest_rate = float(data['interestRate'])
        loan_term = float(data['loanTerm'])

        if loan_amount <= 0 or not (0 < interest_rate <= 100) or not (0 < loan_term <= 200):
            return jsonify({"error": "Invalid input values"}), 400

        simple_interest_year, simple_total_year = calculate_simple_interest(loan_amount, interest_rate, loan_term)
        simple_interest_month = simple_interest_year / (loan_term * 12)
        simple_total_interest = simple_total_year - loan_amount

        compound_interest_year, compound_total_year = calculate_compound_interest(loan_amount, interest_rate, loan_term)
        compound_monthly_payment = compound_total_year / (loan_term * 12)
        compound_total_interest = compound_total_year - loan_amount

        analysis = f"""
**Loan Analysis:**

**Simple Interest:**
- Monthly Interest (approx): ₹{simple_interest_month:.2f}
- Yearly Interest: ₹{simple_interest_year:.2f}
- Total Interest Over Loan Term: ₹{simple_total_interest:.2f}

**Compound Interest (Annual Compounding):**
- Approximate Monthly Payment: ₹{compound_monthly_payment:.2f}
- Total Interest Over Loan Term: ₹{compound_total_interest:.2f}

---

**Repayment Strategies for a Student Loan in India:**

Considering this is a student loan in India, here are some concise and actionable strategies or tips for effective loan repayment:

1.  **Prepayment Focus:** Even small, extra payments can significantly reduce the principal and overall interest paid, especially with a lower interest rate. Explore making prepayments whenever possible from part-time income or savings.

2.  **Budgeting and Prioritization:** Create a strict budget prioritizing loan EMIs. Explore cutting down on non-essential expenses to ensure timely payments and potentially allocate more towards prepayment.

3.  **Explore Government Schemes:** Research current Indian government schemes or subsidies for student loans. Eligibility criteria vary, but it's worth investigating if any benefits apply to your situation. Check the Vidya Lakshmi Portal for information.

4.  **Part-Time Income Utilization:** If earning part-time income, dedicate a significant portion towards loan repayment to accelerate the process and save on interest.

5.  **Maintain Good Credit History:** Timely payments are crucial for building a positive credit score, which will be beneficial for future financial needs.

"""

        return jsonify({"response": analysis})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    try:
        question = data['question']
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400

        prompt = f"""You are a helpful financial assistant located in India, currently assisting a student who has entered details for a loan. Answer the following question concisely and relevantly to their loan scenario. **Please format your answer using bold text for key points and bullet points for lists if applicable.** Question: {question}"""
        response = model.generate_content(prompt)
        return jsonify({"response": response.text.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)