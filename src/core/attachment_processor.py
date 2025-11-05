"""Module for processing JIRA ticket attachments."""
import os
from pathlib import Path
import logging
from typing import List, Dict, Optional
import mimetypes
import requests
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import json

logger = logging.getLogger(__name__)

class AttachmentProcessor:
    """Processes JIRA ticket attachments for enhanced test case generation."""
    
    def __init__(self, output_dir: str):
        """Initialize attachment processor.
        
        Args:
            output_dir: Directory to store downloaded attachments
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def process_attachments(self, attachments: List[Dict]) -> Dict[str, List[Dict]]:
        """Process all attachments from a JIRA ticket.
        
        Args:
            attachments: List of attachment metadata from JIRA
            
        Returns:
            Dict containing processed attachment data by type
        """
        processed_data = {
            'images': [],
            'documents': [],
            'test_data': [],
            'other': []
        }
        
        for attachment in attachments:
            try:
                file_path = self.download_attachment(attachment)
                if not file_path:
                    continue
                    
                mime_type = mimetypes.guess_type(file_path)[0]
                
                if mime_type:
                    if mime_type.startswith('image/'):
                        image_data = self.process_image(file_path)
                        if image_data:
                            processed_data['images'].append(image_data)
                            
                    elif mime_type == 'application/pdf':
                        pdf_data = self.process_pdf(file_path)
                        if pdf_data:
                            processed_data['documents'].append(pdf_data)
                            
                    elif mime_type in ['application/json', 'text/plain']:
                        test_data = self.process_test_data(file_path)
                        if test_data:
                            processed_data['test_data'].append(test_data)
                            
                    else:
                        processed_data['other'].append({
                            'filename': attachment['filename'],
                            'mime_type': mime_type
                        })
                        
            except Exception as e:
                logger.error(f"Error processing attachment {attachment['filename']}: {str(e)}")
                continue
                
        return processed_data
        
    def download_attachment(self, attachment: Dict) -> Optional[Path]:
        """Download attachment from JIRA.
        
        Args:
            attachment: Attachment metadata from JIRA
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            file_path = self.output_dir / attachment['filename']
            
            # Extract credentials from environment
            jira_email = os.getenv('JIRA_EMAIL')
            jira_token = os.getenv('JIRA_API_TOKEN')
            
            if not (jira_email and jira_token):
                raise ValueError("Missing JIRA credentials")
            
            # Create Basic Auth header
            auth = (jira_email, jira_token)
            
            # Download using requests with Basic Auth
            response = requests.get(
                attachment['content'],
                auth=auth,
                verify=True
            )
            response.raise_for_status()
            
            # Save file
            file_path.write_bytes(response.content)
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading {attachment['filename']}: {str(e)}")
            return None
            
    def process_image(self, file_path: Path) -> Optional[Dict]:
        """Process image file for visual test information.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dict containing image analysis or None if failed
        """
        try:
            with Image.open(file_path) as img:
                # Extract text using OCR
                text = pytesseract.image_to_string(img)
                
                return {
                    'filename': file_path.name,
                    'dimensions': img.size,
                    'format': img.format,
                    'extracted_text': text.strip(),
                    'type': 'screenshot' if 'screenshot' in file_path.name.lower() else 'image'
                }
                
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {str(e)}")
            return None
            
    def process_pdf(self, file_path: Path) -> Optional[Dict]:
        """Extract text and information from PDF files.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict containing PDF content or None if failed
        """
        try:
            pdf_document = fitz.open(file_path)
            text_content = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text_content.append(page.get_text())
                
            return {
                'filename': file_path.name,
                'pages': len(pdf_document),
                'content': '\n'.join(text_content)
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return None
            
    def process_test_data(self, file_path: Path) -> Optional[Dict]:
        """Process potential test data files (JSON, text, etc.).
        
        Args:
            file_path: Path to data file
            
        Returns:
            Dict containing parsed data or None if failed
        """
        try:
            content = file_path.read_text()
            
            # Try parsing as JSON
            try:
                data = json.loads(content)
                return {
                    'filename': file_path.name,
                    'type': 'json',
                    'data': data
                }
            except json.JSONDecodeError:
                # Treat as plain text
                return {
                    'filename': file_path.name,
                    'type': 'text',
                    'content': content
                }
                
        except Exception as e:
            logger.error(f"Error processing test data file {file_path}: {str(e)}")
            return None