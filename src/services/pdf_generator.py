from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.textlabels import Label
from datetime import datetime
import os
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import re


class PerformanceReportPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#000000')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#000000')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#000000')
        ))

    def _create_score_chart(self, scores, categories):
        """Create a bar chart for performance scores"""
        plt.figure(figsize=(10, 6))
        bars = plt.bar(categories, scores, color='#ffde5a')
        plt.ylim(0, 100)
        plt.title('Performance Scores', pad=20)
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')

        # Save chart to BytesIO
        img_data = BytesIO()
        plt.savefig(img_data, format='png', bbox_inches='tight', dpi=300)
        img_data.seek(0)
        plt.close()
        return img_data

    def _create_score_table(self, report_data):
        """Create a table with all performance scores"""
        data = [
            ['Category', 'Score'],
            ['Overall Score', str(report_data.overall_score)],
            ['Engagement Level', str(report_data.engagement_level)],
            ['Communication Level', str(report_data.communication_level)],
            ['Objection Handling', str(report_data.objection_handling)],
            ['Adaptability', str(report_data.adaptability)],
            ['Persuasiveness', str(report_data.persuasiveness)],
            ['Create Interest', str(report_data.create_interest)],
            ['Sale Closing', str(report_data.sale_closing)],
            ['Discovery', str(report_data.discovery)],
            ['Cross Selling', str(report_data.cross_selling)],
            ['Solution Fit', str(report_data.solution_fit)]
        ]
        
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Left align first column
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Center align second column
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return table

    def generate_pdf(self, report_data, output_buffer):
        """Generate the complete PDF report"""
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=24,
            bottomMargin=72
        )

        # Build the PDF content
        story = []

        # --- Add logo to the top right ---
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        print("Logo exists:", os.path.exists(logo_path), logo_path)
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=150, height=40)  # Try a smaller size
            logo_table = Table([[logo]], colWidths=[doc.width])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(logo_table)
            # story.append(Spacer(1, 12))
        # --- End logo addition ---

        # Title
        story.append(Paragraph("Performance Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Report Details
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%m-%d-%Y %H:%M:%S')}", self.styles['CustomBody']))
        story.append(Spacer(1, 20))

        # Performance Scores Chart
        story.append(Paragraph("Performance Overview", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        categories = ['Overall', 'Engagement', 'Communication', 'Objection', 'Adaptability', 
                     'Persuasiveness', 'Interest', 'Closing', 'Discovery', 'Cross-Sell', 'Solution']
        scores = [report_data.overall_score, report_data.engagement_level, report_data.communication_level,
                 report_data.objection_handling, report_data.adaptability, report_data.persuasiveness,
                 report_data.create_interest, report_data.sale_closing, report_data.discovery,
                 report_data.cross_selling, report_data.solution_fit]
        
        chart_img = self._create_score_chart(scores, categories)
        story.append(Image(chart_img, width=6*inch, height=3*inch))
        story.append(Spacer(1, 20))

        # Detailed Scores Table
        story.append(Paragraph("Detailed Scores", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        story.append(self._create_score_table(report_data))
        story.append(Spacer(1, 20))

        # Coaching Summary
        story.append(Paragraph("Coaching Summary", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        # Format coaching_summary: every **text** starts on a new line and is bold
        summary = report_data.coaching_summary or ""
        # Replace **text** with <br/><b>text</b>, except at the start
        def replacer(match):
            text = match.group(1)
            return f"<br/><b>{text}</b>"
        # If the summary starts with **text**, don't add <br/> at the very start
        summary = re.sub(r"\*\*(.+?)\*\*", replacer, summary)
        summary = re.sub(r"^(<br/>)", "", summary)  # Remove leading <br/> if present
        story.append(Paragraph(summary, self.styles['CustomBody']))
        story.append(Spacer(1, 20))

        # Footer
        story.append(Paragraph("Generated by Sales AI Coaching System", self.styles['CustomBody']))
        
        # Build the PDF
        doc.build(story)
        return output_buffer 