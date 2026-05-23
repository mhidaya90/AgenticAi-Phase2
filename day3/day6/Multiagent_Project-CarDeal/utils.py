from fpdf import FPDF

def generate_pdf(car_details, final_price, exchange, finance, bank_info=None):
    pdf = FPDF()
    pdf.add_page()

    # Use Unicode font for emojis and multilingual text
    # pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Car Deal Draft", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Car Selected: {car_details['make']} {car_details['model']} ({car_details['year']})", ln=True)
    pdf.cell(200, 10, txt=f"Trim: {car_details['trim']} | Fuel: {car_details['fuel']} | Body: {car_details['body']}", ln=True)
    pdf.cell(200, 10, txt=f"Base Price: {car_details['price']}", ln=True)
    pdf.cell(200, 10, txt=f"Final Negotiated Price: {final_price}", ln=True)

    if exchange:
        pdf.cell(200, 10, txt="Exchange Discount Applied (5%)", ln=True)

    if finance and bank_info is not None:
        pdf.ln(5)
        pdf.cell(200, 10, txt="Finance Details:", ln=True)
        pdf.cell(200, 10, txt=f"Bank: {bank_info['bank_name']}", ln=True)
        pdf.cell(200, 10, txt=f"Loan Amount: {bank_info['loan_amount']}", ln=True)
        pdf.cell(200, 10, txt=f"Tenure: {bank_info['tenure']} months", ln=True)
        pdf.cell(200, 10, txt=f"EMI: {bank_info['emi']}", ln=True)
        pdf.cell(200, 10, txt=f"Processing Fee: {bank_info['processing_fee_pct']}%", ln=True)
        pdf.cell(200, 10, txt=f"Down Payment: {bank_info['down_payment']}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Deal Status: Closed", ln=True)

    # Convert bytearray → bytes for Streamlit
    return bytes(pdf.output(dest="S"))
