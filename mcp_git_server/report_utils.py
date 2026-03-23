"""Utility module for generating PDF reports.

Provides functionality to generate PDF files from code review reports and other content.
"""

from fpdf import FPDF
from datetime import datetime
import os
from typing import Tuple


class CodeReviewPDF(FPDF):
    """Custom PDF class for code review reports with headers and footers."""
    
    def __init__(self, title: str = "Code Review Report"):
        """Initialize the PDF document.
        
        Args:
            title: Title of the PDF document
        """
        super().__init__()
        self.title = title
        self.page_num = 0
    
    def header(self):
        """Add header to each page."""
        # Logo/Title
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, self.title, ln=True, align="C")
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        self.ln(5)
    
    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def export_report_to_pdf(report_content: str, output_path: str, title: str = "Code Review Report") -> Tuple[int, str, str]:
    """Export a code review report to a PDF file.
    
    Converts text content (plain text or markdown-style) into a formatted PDF document
    with professional styling, pagination, and headers/footers.
    
    Args:
        report_content: The text content of the report (can include sections and formatting)
        output_path: Absolute path where the PDF will be saved (e.g., '/path/to/report.pdf')
        title: Title of the PDF document (default: "Code Review Report")
    
    Returns:
        Tuple of (returncode: int, stdout: str, stderr: str)
        - returncode: 0 on success, 1 on failure
        - stdout: Path to the generated PDF on success
        - stderr: Error message on failure
    """
    try:
        # Validate inputs
        if not report_content or not isinstance(report_content, str):
            return 1, '', 'report_content must be a non-empty string'
        
        if not output_path or not isinstance(output_path, str):
            return 1, '', 'output_path must be a valid file path'
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            return 1, '', f'Output directory does not exist: {output_dir}'
        
        # Create PDF
        pdf = CodeReviewPDF(title=title)
        pdf.add_page()
        pdf.set_font("Helvetica", "", 11)
        
        # Process content: split by lines and handle different text sizes
        lines = report_content.split('\n')
        
        for line in lines:
            # Skip empty lines but add spacing
            if not line.strip():
                pdf.ln(3)
                continue
            
            # Detect headers (lines starting with # or ==)
            if line.startswith('#'):
                # Count # symbols for heading level
                heading_level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                
                if heading_level == 1:
                    pdf.set_font("Helvetica", "B", 14)
                    pdf.ln(5)
                    pdf.cell(0, 8, text, ln=True)
                    pdf.ln(2)
                elif heading_level == 2:
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.ln(3)
                    pdf.cell(0, 7, text, ln=True)
                    pdf.ln(1)
                else:
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.cell(0, 6, text, ln=True)
                
                pdf.set_font("Helvetica", "", 11)
                continue
            
            # Detect bullet points
            if line.lstrip().startswith('-') or line.lstrip().startswith('*'):
                text = line.lstrip('- *').strip()
                pdf.set_x(20)  # Indent bullet points
                pdf.cell(0, 6, f"• {text}", ln=True)
                continue
            
            # Detect numbered lists
            if line.lstrip() and line.lstrip()[0].isdigit() and '.' in line.lstrip()[:3]:
                text = line.lstrip()
                # Find the position of the first dot
                dot_pos = text.find('.')
                pdf.set_x(20)  # Indent numbered lists
                pdf.cell(0, 6, text, ln=True)
                continue
            
            # Regular text with multi-line wrapping
            pdf.cell(0, 6, line, ln=True)
        
        # Output PDF to file
        pdf.output(output_path)
        
        # Verify file was created
        if not os.path.exists(output_path):
            return 1, '', f'Failed to create PDF file at {output_path}'
        
        file_size = os.path.getsize(output_path)
        return 0, output_path, ''
    
    except Exception as e:
        return 1, '', f'Error generating PDF: {str(e)}'


def export_text_to_pdf(text_content: str, output_path: str, title: str = "Report") -> Tuple[int, str, str]:
    """Export plain text content to a PDF file.
    
    Simple conversion of plain text to PDF with basic formatting.
    
    Args:
        text_content: The text content to export
        output_path: Absolute path where the PDF will be saved
        title: Title of the PDF document
    
    Returns:
        Tuple of (returncode: int, stdout: str, stderr: str)
    """
    return export_report_to_pdf(text_content, output_path, title)
