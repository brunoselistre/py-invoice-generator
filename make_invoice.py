import json
import os
from datetime import datetime, timedelta
from fpdf import FPDF, XPos, YPos

# Constants
LABEL_WIDTH = 60
VALUE_WIDTH = 120

HOURLY_RATE = 21.880000000000000000001

class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 10, "INVOICE", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def add_section(self, title, data):
        """Add a section with title and key-value data to the PDF."""
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

        self.set_font("Helvetica", "", 11)
        for label, value in data.items():
            self.cell(LABEL_WIDTH, 8, f"{label}:", border=0, align="L")
            self.cell(VALUE_WIDTH, 8, value, border=0, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
        self.ln(7) 
    
    def add_table(self, title, header, data):
        """Add a table with title, header, and data to the PDF, ensuring all cells have the same height."""
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)  # Table title
        self.ln(1)

        self.set_font("Helvetica", "B", 11)
        col_widths = [80, 25, 40, 40]  # Define column widths
        line_height = 6  # Standard line height per row

        # Print header row
        for col_name, col_width in zip(header, col_widths):
            self.cell(col_width, 8, col_name, border=1, align="C")

        self.ln()
        self.set_font("Helvetica", "", 11)

        for row in data:
            quantidade = float(row[1])
            valor_unitario = float(row[2])
            row[3] = "{:.2f}".format(quantidade * valor_unitario)  # Compute total

            # First pass: Determine the max row height
            cell_heights = []
            for item, col_width in zip(row, col_widths):
                text = str(item)
                text_width = self.get_string_width(text)
                num_lines = max(1, int(text_width / col_width) + 1)  # Ensure at least 1 line
                cell_heights.append(num_lines * line_height)

            max_row_height = max(cell_heights)  # Get tallest cell height in this row

            # Second pass: Draw each cell with the same row height
            y_start = self.get_y()
            for item, col_width in zip(row, col_widths):
                x_start = self.get_x()
                
                # Draw a fixed-size cell (with border) to ensure alignment
                self.multi_cell(col_width, line_height, str(item), border=0, align="L")
                
                # Manually draw a full-height border
                self.rect(x_start, y_start, col_width, max_row_height)

                # Reset X position for next column
                self.set_xy(x_start + col_width, y_start)

            self.ln(max_row_height)  # Move to next row

        self.ln(7)  # Spacing after the table


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
        if current_day.weekday() < 5:  # Monday to Friday are business days
            business_days += 1
        current_day += timedelta(days=1)

    return business_days

def get_invoice_number():
    """Returns the next invoice number with five-digit formatting."""
    
    folder_path = "invoices"
    invoices_count = sum(1 for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)))
    invoices_count += 1  # Increment to get the next invoice number

    return "DVT{:05d}".format(invoices_count)


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

current_date    = datetime.today().strftime("%d/%m/%Y")
current_year    = datetime.today().year
current_month   = datetime.today().month
expiration_date = last_day_of_month()

# Calculate the number of business days for the current month
business_days  = get_business_days_in_month(current_year, current_month)
invoice_number = get_invoice_number()

# Prompt user for time-off (days)
try:
    time_off = int(input("Time-off (days)? "))
    business_days -= time_off
    quantidade = business_days * 8  # Assuming 8 hours per business day
except ValueError:
    print("Invalid input. Time-off should be an integer.")
    quantidade = business_days * 8 

# Load invoice variables from JSON file
invoice_variables = load_invoice_variables()

# Create PDF instance
pdf = InvoicePDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Add sections and tables to PDF
pdf.add_section("INFORMAÇÕES DA FATURA", {
    "Número da Fatura": invoice_number,
    "Data de Emissão":  current_date,
    "Vencimento":       str(expiration_date.strftime("%d/%m/%Y")),
})


if "provider_data" in invoice_variables:
    pdf.add_section("DADOS DO PRESTADOR DE SERVIÇO", invoice_variables["provider_data"])

if "client_data" in invoice_variables:
    pdf.add_section("DADOS DO CLIENTE", invoice_variables["client_data"])

if "service_description" in invoice_variables:
    pdf.add_table(
        "DESCRIÇÃO DOS SERVIÇOS PRESTADOS", 
        ["Descrição do Serviço", "Quantidade", "Valor Unitário (EUR)", "Total (EUR)"], 
        [[invoice_variables["service_description"], str(quantidade), HOURLY_RATE, "0.00"]]
    )

if "payment_data" in invoice_variables:
    pdf.add_section("FORMA DE PAGAMENTO", invoice_variables["payment_data"])

invoice_filename = f"invoices/invoice_{datetime.today().strftime('%m_%y')}.pdf"
pdf.output(invoice_filename)

print(f"\nInvoice PDF: {invoice_filename}")
print("Business days current month:", business_days)
