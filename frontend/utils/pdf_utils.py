import io
import pandas as pd
from fpdf import FPDF

class PDFReport(FPDF):
    def __init__(self, title="RetainAI Report"):
        super().__init__()
        self.report_title = title

    def header(self):
        self.set_font("helvetica", 'B', 15)
        self.cell(0, 10, text=self.report_title, align='C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", 'I', 8)
        self.cell(0, 10, text=f'Page {self.page_no()}', align='C')

def _sanitize(text: str) -> str:
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def create_pdf_report(title: str, text_content: str) -> bytes:
    pdf = PDFReport(title=_sanitize(title))
    pdf.add_page()
    pdf.set_font("helvetica", size=11)
    
    pdf.multi_cell(0, 8, text=_sanitize(text_content))
        
    return bytes(pdf.output())

def create_pdf_table(title: str, df: pd.DataFrame) -> bytes:
    pdf = PDFReport(title=_sanitize(title))
    pdf.add_page()
    
    if df.empty:
        pdf.set_font("helvetica", size=10)
        pdf.cell(0, 10, text="No data available")
        return bytes(pdf.output())
        
    pdf.set_font("helvetica", size=9)
    with pdf.table() as table:
        # Header
        row = table.row()
        for col in df.columns:
            row.cell(_sanitize(str(col)))
        # Data
        for _, df_row in df.iterrows():
            row = table.row()
            for item in df_row:
                row.cell(_sanitize(str(item)))
                
    return bytes(pdf.output())

def create_pdf_from_csv(title: str, csv_string: str) -> bytes:
    df = pd.read_csv(io.StringIO(csv_string))
    # Cap to 500 rows to prevent mega-PDF generation hanging the server
    if len(df) > 500:
        df = df.head(500)
    return create_pdf_table(title, df)
