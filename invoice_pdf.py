from fpdf import FPDF, XPos, YPos

class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 10, "INVOICE", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def add_section(self, title, data):
        """Add a section with title and key-value data to the PDF."""
        LABEL_WIDTH = 60
        VALUE_WIDTH = 120

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
