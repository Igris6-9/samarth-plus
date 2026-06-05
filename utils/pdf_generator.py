from fpdf import FPDF
import io

# 👑 DAKASH ENGINE - HYBRID PDF ARCHITECTURE
class SamarthPDF(FPDF):
    def header(self):
        # Branding - PC/Mobile Printable Format
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 180, 255) # Deep Neon Cyan
        self.cell(0, 10, 'SAMARTH - MISSION REPORT', 0, 1, 'C')
        
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Verified by Dakash Divine Engine Core', 0, 1, 'C')
        self.ln(10)
        
        # Border for the page
        self.rect(5, 5, 200, 287)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Secured Identity: {self.page_no()} | System v2.4', 0, 0, 'C')

def generate_result_pdf(user_name, subject, score, total, rank, suggestions):
    """
    Cadet ka Performance Certificate/Report generate karna.
    """
    pdf = SamarthPDF()
    pdf.add_page()
    
    # 👤 User Banner
    pdf.set_fill_color(230, 245, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 12, f" CADET CODENAME: {user_name.upper()}", 1, 1, 'L', fill=True)
    pdf.ln(5)

    # 📊 Mission Stats Table
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, "MISSION PERFORMANCE LOG", 0, 1, 'L')
    
    pdf.set_font('Arial', '', 11)
    accuracy = (score/total)*100 if total > 0 else 0
    
    # Table Styling
    data = [
        ["Target Subject", subject],
        ["Neural Score", f"{score} / {total}"],
        ["Efficiency Rate", f"{accuracy:.1f}%"],
        ["Assigned Rank", rank]
    ]

    for row in data:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(70, 10, row[0], 1, 0, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.cell(120, 10, row[1], 1, 1, 'L')

    # 🧠 AI Insight Block
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(188, 19, 254) # Divine Purple
    pdf.cell(0, 10, "SAMARTH AI - STRATEGIC ANALYSIS", 0, 1, 'L')
    
    pdf.set_font('Arial', 'I', 11)
    pdf.set_text_color(60, 60, 60)
    # multi_cell is best for long AI suggestions (Automatic wrap)
    pdf.multi_cell(0, 8, f"Engine Output: {suggestions}")

    # Memory buffer support for Flask
    return pdf.output(dest='S').encode('latin-1')

def generate_timetable_pdf(schedule_data):
    """
    AI Schedule ko printable format mein convert karna.
    """
    pdf = SamarthPDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 100, 200)
    pdf.cell(0, 15, "DAILY COMBAT STRATEGY", 0, 1, 'C')
    pdf.ln(5)

    # Table Header
    pdf.set_fill_color(0, 180, 255)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(45, 12, "TIME SLOT", 1, 0, 'C', fill=True)
    pdf.cell(145, 12, "MISSION DETAILS", 1, 1, 'C', fill=True)

    # Table Content
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    
    for item in schedule_data:
        # Auto-height calculation for long tasks
        pdf.cell(45, 10, item['time'], 1, 0, 'C')
        pdf.cell(145, 10, f"{item['task']} - {item['detail']}", 1, 1, 'L')

    return pdf.output(dest='S').encode('latin-1')
