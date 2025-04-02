# Invoice Generator

This script generates an invoice in PDF format based on business days within the current month and user-defined variables. It calculates working hours, assigns an invoice number, and formats the invoice details before saving the PDF.

## Features
- Automatically calculates the number of business days in the current month.
- Allows the user to specify the number of holidays (non-working days).
- Loads invoice variables such as provider and client details from a JSON file.
- Generates a structured PDF invoice with relevant details.
- Saves invoices with a formatted filename in the `invoices` folder.

## Requirements
### Dependencies
Ensure you have the following Python modules installed before running the script:

```sh
pip install -r requirements.txt
```

## Usage
1. Prepare an `invoice_variables.json` file with the necessary data (e.g., provider, client, and payment details).
2. Run the script:
   ```sh
   python invoice_generator.py
   ```
3. Enter the number of holidays when prompted.
4. The generated invoice will be saved in the `invoices` folder.

## Configuration
### Invoice Variables (`invoice_variables.json`)
This file should contain necessary details in the following format:
```json
{
  "hourly_rate": 50.00,
  "service_description": "Consulting Services",
  "provider_data": {
    "Nome": "Your Name or Business",
    "Endereço": "Street, City, ZIP Code"
  },
  "client_data": {
    "Nome": "Client Name",
    "Endereço": "Client Address"
  },
  "payment_data": {
    "Método": "Bank Transfer",
    "IBAN": "XX123456789"
  }
}
```

## Output
The script generates an invoice PDF file named `invoice_MM_YY.pdf` (e.g., `invoices/invoice_04_25.pdf`).

## Notes
- The invoice number is auto-generated and follows the format `DVT00001`, incrementing with each new invoice.
- The script assumes an 8-hour workday for calculations.

## License
This project is open-source and can be modified as needed.
s