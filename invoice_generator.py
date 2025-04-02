import os
import json
import invoice_pdf

from datetime import datetime, timedelta

def load_invoice_variables(filename='invoice_variables.json'):
    """Load external invoice variables from a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{filename}'.")
        return {}
    
def last_day_of_month():
    """Returns the last day of the current month."""
    next_month = datetime.today().replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

def get_business_days_in_month(year, month):
    """Returns the number of business days in a given month."""
    first_day = datetime(year, month, 1)
    last_day  = datetime(year, month + 1, 1) - timedelta(days=1) if month != 12 else datetime(year, month, 31)

    business_days = 0
    current_day = first_day
    while current_day <= last_day:
        if current_day.weekday() < 5:
            business_days += 1
        current_day += timedelta(days=1)

    return business_days

def get_invoice_number(folder_path):
    """Returns the next invoice number with five-digit formatting."""
    invoices_count = sum(1 for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)))
    invoices_count += 1  # Increment to get the next invoice number

    return "DVT{:05d}".format(invoices_count)

def main():
    business_days  = get_business_days_in_month(datetime.today().year, datetime.today().month)

    # Prompt user for Holidays (days)
    try:
        time_off = int(input("Holidays (days)? "))
        business_days -= time_off
        quantidade = business_days * 8  # Assuming 8 hours per business day
    except ValueError:
        print("Invalid input. Holidays should be an integer.")
        quantidade = business_days * 8 

    invoices_folder = "invoices"
    os.makedirs(invoices_folder, exist_ok=True)
    invoice_variables = load_invoice_variables()
    
    pdf = invoice_pdf.InvoicePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.add_section("INFORMAÇÕES DA FATURA", {
        "Número da Fatura": get_invoice_number(invoices_folder),
        "Data de Emissão":  datetime.today().strftime("%d/%m/%Y"), # Current date
        "Vencimento":       str(last_day_of_month().strftime("%d/%m/%Y")),
    })

    if "provider_data" in invoice_variables:
        pdf.add_section("DADOS DO PRESTADOR DE SERVIÇO", invoice_variables["provider_data"])

    if "client_data" in invoice_variables:
        pdf.add_section("DADOS DO CLIENTE", invoice_variables["client_data"])

    if "service_description" in invoice_variables:
        pdf.add_table(
            "DESCRIÇÃO DOS SERVIÇOS PRESTADOS", 
            ["Descrição do Serviço", "Quantidade", "Valor Unitário (EUR)", "Total (EUR)"], 
            [[invoice_variables["service_description"], str(quantidade), invoice_variables["hourly_rate"], "0.00"]]
        )

    if "payment_data" in invoice_variables:
        pdf.add_section("FORMA DE PAGAMENTO", invoice_variables["payment_data"])


    invoice_filename = f"{invoices_folder}/invoice_{datetime.today().strftime('%m_%y')}.pdf"
    pdf.output(invoice_filename)

    print(f"\nInvoice PDF: {invoice_filename}")
    print("Business days current month:", business_days)


if __name__=="__main__":
    main()