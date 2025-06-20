import os
import tempfile
import PyPDF2
import docx
import google.generativeai as genai
from datetime import datetime
from typing import Dict, Optional, BinaryIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessingDAL:
    def __init__(self, api_key: str):
        """
        Initialize the Document Processing DAL with Google Gemini API

        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Document processor initialized with Gemini 2.5 Flash")

    def extract_pdf_content(self, file_path: str) -> Dict:
        """
        Extract content from PDF file

        Args:
            file_path (str): Path to the PDF file

        Returns:
            Dict: Extracted content with metadata
        """
        content = {
            'text': '',
            'pages': 0,
            'tables_detected': False,
            'extraction_method': 'PDF'
        }

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content['pages'] = len(pdf_reader.pages)

                full_text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            full_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                        continue

                content['text'] = full_text.strip()

                # Simple table detection
                table_indicators = ['|', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼']
                content['tables_detected'] = any(indicator in content['text'] for indicator in table_indicators)

            logger.info(f"PDF processed: {content['pages']} pages, {len(content['text'])} characters")
            return content

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise Exception(f"Failed to extract PDF content: {str(e)}")

    def extract_docx_content(self, file_path: str) -> Dict:
        """
        Extract content from DOCX file

        Args:
            file_path (str): Path to the DOCX file

        Returns:
            Dict: Extracted content with metadata
        """
        content = {
            'text': '',
            'paragraphs': 0,
            'tables_detected': False,
            'tables_content': [],
            'extraction_method': 'DOCX'
        }

        try:
            doc = docx.Document(file_path)

            # Extract text from paragraphs
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text.strip())

            content['text'] = '\n\n'.join(paragraphs)
            content['paragraphs'] = len(paragraphs)

            # Extract tables
            if doc.tables:
                content['tables_detected'] = True
                tables_text = []

                for i, table in enumerate(doc.tables):
                    table_data = []
                    for row in table.rows:
                        row_data = []
                        for cell in row.cells:
                            row_data.append(cell.text.strip())
                        table_data.append(row_data)

                    # Convert table to text format
                    table_text = f"\n--- Table {i + 1} ---\n"
                    for row in table_data:
                        table_text += " | ".join(row) + "\n"

                    tables_text.append(table_text)
                    content['tables_content'].append(table_data)

                # Append tables to main text
                content['text'] += '\n\n' + '\n'.join(tables_text)

            logger.info(f"DOCX processed: {content['paragraphs']} paragraphs, {len(doc.tables)} tables")
            return content

        except Exception as e:
            logger.error(f"Error processing DOCX: {str(e)}")
            raise Exception(f"Failed to extract DOCX content: {str(e)}")

    def analyze_with_gemini(self, content: Dict) -> str:
        """
        Analyze document content using Google Gemini AI

        Args:
            content (Dict): Document content and metadata

        Returns:
            str: AI-generated analysis summary
        """
        try:
            if not content.get('text') or len(content['text'].strip()) < 50:
                return "Document content is too short or empty for meaningful analysis."

            prompt = f"""
You are a senior sales analyst providing a comprehensive professional summary of this sales document. Write a detailed, structured summary that a C-level executive would expect to see.

Document Content:
{content['text']}

Document Metadata:
- Extraction Method: {content.get('extraction_method', 'Unknown')}
- Pages/Paragraphs: {content.get('pages', content.get('paragraphs', 'Unknown'))}
- Tables Detected: {content.get('tables_detected', False)}

Provide a professional sales analysis summary that includes:

EXECUTIVE OVERVIEW: Brief description of document type, purpose, and strategic context.

FINANCIAL PERFORMANCE: All revenue figures, sales targets, pricing data, profit margins, cost analysis, budget allocations, and financial KPIs with specific numbers and percentages.

SALES METRICS & ANALYTICS: Conversion rates, pipeline data, sales cycle length, win/loss ratios, quota attainment, territory performance, year-over-year comparisons, and growth metrics.

PRODUCT/SERVICE PORTFOLIO: Detailed breakdown of products or services discussed, including pricing strategies, market positioning, competitive advantages, feature sets, and performance by product line.

CUSTOMER INTELLIGENCE: Client profiles, account values, customer segments, retention rates, churn analysis, customer acquisition costs, lifetime value, and market demographics.

MARKET ANALYSIS: Territory coverage, market share data, competitive landscape, industry trends, market opportunities, and geographic performance.

OPERATIONAL INSIGHTS: Sales team performance, resource allocation, process efficiency, bottlenecks, and operational recommendations.

STRATEGIC RECOMMENDATIONS: Priority actions, improvement opportunities, risk mitigation, resource needs, and next steps for sales optimization.

Write in a formal, professional tone suitable for senior management review. Include all quantitative data with context and implications. Ensure the summary provides actionable business intelligence for sales leadership decision-making.

If the document doesn't contain sales-related content, provide a general business analysis following the same structured approach but adapted to the document's actual content.
"""

            response = self.model.generate_content(prompt)

            if not response or not response.text:
                raise Exception("Empty response from Gemini API")

            return response.text

        except Exception as e:
            logger.error(f"Error analyzing with Gemini: {str(e)}")
            raise Exception(f"Failed to analyze document with AI: {str(e)}")

    def process_document(self, file_data: BinaryIO, filename: str) -> Dict:
        """
        Process uploaded document and return analysis

        Args:
            file_data (BinaryIO): File data stream
            filename (str): Original filename

        Returns:
            Dict: Processing result with summary
        """
        temp_file_path = None

        try:
            logger.info(f"Starting document processing: {filename}")

            # Validate file type
            if not filename.lower().endswith(('.pdf', '.docx', '.doc')):
                raise ValueError(f"Unsupported file type. Only PDF and DOCX files are supported. Got: {filename}")

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file_path = temp_file.name

                # Write uploaded file data to temporary file
                temp_file.write(file_data.read())
                temp_file.flush()

            # Extract content based on file type
            if filename.lower().endswith('.pdf'):
                content = self.extract_pdf_content(temp_file_path)
            elif filename.lower().endswith(('.docx', '.doc')):
                content = self.extract_docx_content(temp_file_path)
            else:
                raise ValueError(f"Unsupported file type: {filename}")

            # Analyze with AI
            summary = self.analyze_with_gemini(content)

            # Prepare successful result
            result = {
                'filename': filename,
                'processing_timestamp': datetime.now().isoformat(),
                'file_size_kb': round(len(file_data.getvalue()) / 1024, 2) if hasattr(file_data, 'getvalue') else 0,
                'document_metadata': {
                    'extraction_method': content['extraction_method'],
                    'pages': content.get('pages', content.get('paragraphs', 0)),
                    'tables_detected': content.get('tables_detected', False),
                    'content_length': len(content['text']),
                    'has_content': len(content['text'].strip()) > 0
                },
                'summary': summary,
                'success': True,
                'error': None
            }

            logger.info(f"Document processing completed successfully: {filename}")
            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Document processing failed for {filename}: {error_msg}")

            return {
                'filename': filename,
                'processing_timestamp': datetime.now().isoformat(),
                'summary': None,
                'success': False,
                'error': error_msg,
                'document_metadata': None
            }

        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_file_path}: {str(e)}")

    def validate_document(self, file_data: BinaryIO, filename: str) -> Dict:
        """
        Validate document before processing

        Args:
            file_data (BinaryIO): File data stream
            filename (str): Original filename

        Returns:
            Dict: Validation result
        """
        try:
            # Check file extension
            if not filename.lower().endswith(('.pdf', '.docx', '.doc')):
                return {
                    'valid': False,
                    'error': f"Unsupported file type. Only PDF and DOCX files are supported. Got: {filename}"
                }

            # Check file size (limit to 10MB)
            file_size = len(file_data.read())
            file_data.seek(0)  # Reset file pointer

            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return {
                    'valid': False,
                    'error': f"File size too large. Maximum size is 10MB. Got: {round(file_size / (1024*1024), 2)}MB"
                }

            if file_size == 0:
                return {
                    'valid': False,
                    'error': "File is empty"
                }

            return {
                'valid': True,
                'file_size_mb': round(file_size / (1024*1024), 2),
                'file_type': os.path.splitext(filename)[1].lower()
            }

        except Exception as e:
            return {
                'valid': False,
                'error': f"Validation error: {str(e)}"
            }