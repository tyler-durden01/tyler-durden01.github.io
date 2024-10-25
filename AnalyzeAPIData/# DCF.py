import openpyxl
import pandas as pd

def duplicate_excel_file(original_file, duplicate_file):
    # Open the original Excel file
    wb = openpyxl.load_workbook(original_file)

    # Save a copy of the original Excel file with a new name
    wb.save(duplicate_file)

    print(f"Excel file duplicated successfully as '{duplicate_file}'.")

# Example usage
original_file = "DCF_Template.xlsx"
duplicate_file = f'{ticker}_DCF.xlsx'

duplicate_excel_file(original_file, duplicate_file)