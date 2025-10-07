"""
CV Enhancement Agent using LangGraph

This agent provides comprehensive CV enhancement services including:
- JD alignment and content refinement
- Company and contact anonymization
- Portfolio and project enhancement
- Professional formatting
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, TypedDict, Union

import openai
from jinja2 import Environment, FileSystemLoader
from langgraph.graph import END, StateGraph

from common.settings import config
from core.document_loader import FileType, load_document
from lib.utils import get_access_token_from_copilot

logger = logging.getLogger(__name__)


class CVState(TypedDict):
    """State for CV enhancement workflow."""

    file_path: str
    job_description: str
    additional_input: Optional[Union[str, Dict]]
    cv_content: str
    enhanced_content: str
    output_path: str
    generate_pdf: bool
    include_logo: bool


class CVEnhancementAgent:
    """LangGraph-based agent for enhancing CVs."""

    def __init__(self):
        """Initialize the CV enhancement agent."""
        self.jinja_env = Environment(
            loader=FileSystemLoader("templates"), autoescape=True
        )
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """Build LangGraph workflow for CV enhancement."""
        workflow = StateGraph(CVState)

        # Add nodes
        workflow.add_node("load_document", self._load_document_node)
        workflow.add_node("enhance_content", self._enhance_content_node)
        workflow.add_node("generate_output", self._generate_output_node)

        # Define edges
        workflow.set_entry_point("load_document")
        workflow.add_edge("load_document", "enhance_content")
        workflow.add_edge("enhance_content", "generate_output")
        workflow.add_edge("generate_output", END)

        return workflow.compile()

    def _load_document_node(self, state: CVState) -> CVState:
        """Load CV document from file path or URL."""
        try:
            file_type = self._detect_file_type(state["file_path"])
            documents = load_document(state["file_path"], file_type)
            cv_content = "\n\n".join([doc.page_content for doc in documents])

            logger.info(
                f"Loaded {len(documents)} document(s) from {state['file_path']}"
            )
            logger.info(f"CV content length: {len(cv_content)} chars")
            logger.debug(f"CV content preview: {cv_content[:200]}...")

            if not cv_content.strip():
                logger.warning("Loaded CV content is empty!")

            return {**state, "cv_content": cv_content}
        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            raise

    def _enhance_content_node(self, state: CVState) -> CVState:
        """Enhance CV content using AI."""
        try:
            prompt = self._create_enhancement_prompt(
                state["cv_content"],
                state["job_description"],
                state.get("additional_input"),
            )

            client = self._setup_openai_client()
            response = client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert CV enhancement specialist with deep knowledge of recruitment, ATS systems, and professional presentation.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            enhanced_content = response.choices[0].message.content
            if not enhanced_content:
                raise ValueError("Empty response from AI model")

            logger.info(f"CV enhancement completed successfully (length: {len(enhanced_content)} chars)")
            logger.debug(f"Enhanced content preview: {enhanced_content[:200]}...")

            return {**state, "enhanced_content": enhanced_content}

        except Exception as e:
            logger.error(f"Content enhancement failed: {e}")
            raise

    def _generate_output_node(self, state: CVState) -> CVState:
        """Generate final resume file (HTML/PDF)."""
        try:
            # Debug: Check if enhanced content exists
            if not state.get("enhanced_content", "").strip():
                logger.error("Enhanced content is empty! Using original CV content as fallback.")
                # Fallback to original content if enhancement failed
                content_to_use = state.get("cv_content", "No content available")
            else:
                content_to_use = state["enhanced_content"]
                logger.info(f"Using enhanced content (length: {len(content_to_use)} chars)")

            # Get logo path if needed
            logo_path = None
            if state.get("include_logo", True):
                logo_path = os.path.join(os.getcwd(), "assets", "brainium-logo.svg")

            # Generate HTML content
            template = self.jinja_env.get_template("resume_template.md")
            html_content = template.render(
                cv_content=content_to_use,
                logo_path=logo_path,
                include_logo=state.get("include_logo", True),
            )

            output_path = Path(state["output_path"])
            
            # Always create HTML first for debugging
            html_path = output_path.with_suffix(".html")
            html_path.write_text(html_content, encoding="utf-8")
            logger.info(f"HTML file created: {html_path}")

            if state.get("generate_pdf", False):
                # Generate PDF with multiple fallback options
                pdf_path = output_path.with_suffix(".pdf")
                pdf_generated = self._generate_pdf_with_fallbacks(html_content, pdf_path, state)
                
                if pdf_generated:
                    logger.info(f"PDF successfully generated: {pdf_path}")
                else:
                    logger.warning(f"PDF generation failed, using HTML: {html_path}")
            
            return state

        except Exception as e:
            logger.error(f"Output generation failed: {e}")
            raise

    def _generate_pdf_with_fallbacks(self, html_content: str, pdf_path: Path, state: CVState) -> bool:
        """Generate PDF using multiple methods with fallbacks."""
        
        # Method 1: Try markdown + xhtml2pdf (clean and simple) - Primary method
        try:
            import markdown
            from xhtml2pdf import pisa
            import os
            
            logger.info(f"Using markdown + xhtml2pdf for clean PDF generation")
            
            # Extract and convert HTML content to markdown
            markdown_content = self._html_to_markdown(html_content)
            
            # Convert markdown to HTML with proper extensions
            html = markdown.markdown(
                markdown_content, extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
            )
            
            # Check if logo should be included
            logo_html = ""
            if state.get("include_logo", False):
                logo_path = os.path.join(os.getcwd(), "assets", "brainium-logo.svg")
                if os.path.exists(logo_path):
                    try:
                        # Try to convert SVG to base64 for embedding
                        import base64
                        with open(logo_path, 'rb') as logo_file:
                            logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
                            logo_html = f'''
                            <div style="text-align: left; margin-bottom: 20px; border-bottom: 1px solid #e0e0e0; padding-bottom: 15px;">
                                <img src="data:image/svg+xml;base64,{logo_data}" alt="Brainium Logo" style="max-width: 150px; height: auto;">
                            </div>
                            '''
                            logger.info("Logo embedded as base64")
                    except Exception as e:
                        logger.warning(f"Could not embed SVG logo: {e}")
                        # Fallback to text logo
                        logo_html = f'''
                        <div style="text-align: left; margin-bottom: 20px; border-bottom: 1px solid #e0e0e0; padding-bottom: 15px;">
                            <div style="font-size: 18px; font-weight: bold; color: #cc0000;">BRAINIUM</div>
                        </div>
                        '''
                        logger.info("Using text logo as fallback")

            # Add CSS styling for better PDF formatting (based on your working example)
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.4;
                        margin: 20px;
                        color: #333;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #2c3e50;
                        margin-top: 15px;
                        margin-bottom: 8px;
                    }}
                    h1 {{
                        font-size: 28px;
                        text-align: left;
                        margin-top: 0;
                        margin-bottom: 10px;
                    }}
                    h2 {{
                        font-size: 18px;
                        margin-top: 20px;
                        margin-bottom: 8px;
                    }}
                    ul, ol {{
                        margin: 5px 0;
                        padding-left: 20px;
                    }}
                    li {{
                        margin: 2px 0;
                        line-height: 1.3;
                    }}
                    ul li {{
                        list-style-type: disc;
                    }}
                    ul li ul li {{
                        list-style-type: circle;
                    }}
                    p {{
                        margin: 5px 0;
                    }}
                    strong {{
                        color: #2c3e50;
                    }}
                    code {{
                        background-color: #f8f9fa;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: monospace;
                    }}
                </style>
            </head>
            <body>
            {logo_html}
            {html}
            </body>
            </html>
            """

            with open(pdf_path, "wb") as f:
                pisa.CreatePDF(styled_html, dest=f)
            
            logger.info(f"PDF generated using markdown + xhtml2pdf: {pdf_path}")
            return True
            
        except Exception as e:
            logger.warning(f"markdown + xhtml2pdf generation failed: {e}")
        
        # Method 2: Try reportlab (pure Python PDF generation) - Fallback method
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
            
            # Create PDF using reportlab
            doc = SimpleDocTemplate(str(pdf_path), pagesize=letter,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            styles = getSampleStyleSheet()
            
            # Extract and process enhanced content (not HTML template)
            enhanced_content = self._extract_enhanced_content(html_content)
            
            # Create story (content) for PDF
            story = []
            
            # Process content line by line
            lines = enhanced_content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 6))
                    continue
                    
                # Detect different content types
                if line.startswith('**') and line.endswith('**'):
                    # Bold headers
                    header_text = line.replace('**', '').strip()
                    if len(header_text) < 30:  # Short headers = main titles
                        story.append(Paragraph(header_text, styles['Title']))
                    else:  # Longer headers = subtitles
                        story.append(Paragraph(header_text, styles['Heading1']))
                elif line.startswith('---'):
                    # Separators
                    story.append(Spacer(1, 12))
                elif line.startswith('- '):
                    # Bullet points
                    bullet_text = line[2:]  # Remove '- '
                    story.append(Paragraph(f"• {bullet_text}", styles['Normal']))
                elif line.replace(' ', '').replace('-', '').replace('_', '').isalnum() and len(line) < 50:
                    # Section headers (short lines, mostly alphanumeric)
                    story.append(Paragraph(line, styles['Heading2']))
                else:
                    # Regular text
                    story.append(Paragraph(line, styles['Normal']))
                
                story.append(Spacer(1, 6))
            
            doc.build(story)
            
            logger.info(f"PDF generated using reportlab: {pdf_path}")
            return True
            
        except Exception as e:
            logger.warning(f"reportlab failed: {e}")

        # Method 3: Try PyMuPDF (fallback)
        try:
            import fitz  # PyMuPDF
            
            # Create a simple PDF with formatted text
            doc = fitz.open()  # create new PDF
            page = doc.new_page() # type: ignore  # Create a new page (PyMuPDF method)
            
            # Extract and clean text content from HTML
            text_content = self._html_to_text(html_content)
            
            # Format the text nicely in the PDF
            self._add_formatted_text_to_pdf(page, text_content)
            
            doc.save(str(pdf_path))
            doc.close()
            
            logger.info(f"PDF generated using PyMuPDF: {pdf_path}")
            return True
            
        except Exception as e:
            logger.warning(f"PyMuPDF failed: {e}")

        # All methods failed
        logger.error("All PDF generation methods failed")
        return False
    
    def _extract_enhanced_content(self, html_content: str) -> str:
        """Extract just the enhanced CV content from HTML template."""
        import re
        
        # Find content between <div class="content"> tags
        content_match = re.search(r'<div class="content">\s*(.*?)\s*</div>', html_content, re.DOTALL | re.IGNORECASE)
        if content_match:
            return content_match.group(1).strip()
        
        # Fallback: extract content after </style> and before </body>
        style_end = html_content.find('</style>')
        body_end = html_content.find('</body>')
        if style_end != -1 and body_end != -1:
            content_section = html_content[style_end + 8:body_end]
            # Remove HTML tags but keep the enhanced content
            content_section = re.sub(r'<[^>]+>', '', content_section)
            return content_section.strip()
        
        # Last resort: return original content
        return self._html_to_text(html_content)
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to clean text."""
        import re
        
        # Remove HTML tags but preserve structure
        text = html_content
        
        # Convert common HTML elements to text
        text = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n\1\n', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<li[^>]*>(.*?)</li>', r'• \1\n', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'\1', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<b[^>]*>(.*?)</b>', r'\1', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
        text = text.strip()
        
        return text
    
    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to clean markdown."""
        
        # First extract the enhanced content
        enhanced_content = self._extract_enhanced_content(html_content)
        
        # If it's already mostly markdown-like, return it
        if not '<' in enhanced_content:
            return enhanced_content
        
        import re
        
        # Convert HTML to markdown
        markdown = enhanced_content
        
        # Convert headers
        markdown = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert paragraphs
        markdown = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', markdown, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert lists
        markdown = re.sub(r'<ul[^>]*>', '', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'</ul>', '', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert bold/strong
        markdown = re.sub(r'<(strong|b)[^>]*>(.*?)</(strong|b)>', r'**\2**', markdown, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert italic/em
        markdown = re.sub(r'<(em|i)[^>]*>(.*?)</(em|i)>', r'*\2*', markdown, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert breaks
        markdown = re.sub(r'<br[^>]*>', '\n', markdown, flags=re.IGNORECASE)
        
        # Remove remaining HTML tags
        markdown = re.sub(r'<[^>]+>', '', markdown)
        
        # Clean up whitespace
        markdown = re.sub(r'\n\s*\n', '\n\n', markdown)  # Multiple newlines to double
        markdown = re.sub(r'[ \t]+', ' ', markdown)  # Multiple spaces to single
        markdown = markdown.strip()
        
        return markdown
    
    def _add_formatted_text_to_pdf(self, page, text_content: str):
        """Add formatted text to PDF page using PyMuPDF."""
        import fitz  # Import here to handle missing dependency gracefully
        
        font_size = 11
        line_height = 14
        margin = 72  # 1 inch
        page_width = page.rect.width
        page_height = page.rect.height
        
        lines = text_content.split('\n')
        y_position = page_height - margin
        
        for line in lines:
            line = line.strip()
            if not line:
                y_position -= line_height * 0.5  # Smaller space for empty lines
                continue
                
            # Check if it's a header (all caps or short line)
            if line.isupper() or len(line) < 50:
                current_font_size = font_size + 2
                # Use flags if available, otherwise skip
                try:
                    font_flags = fitz.TEXT_FONT_BOLD
                except AttributeError:
                    font_flags = 0
            else:
                current_font_size = font_size
                font_flags = 0
            
            # Word wrap long lines
            words = line.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                
                # Estimate text width (simple approach)
                char_width = current_font_size * 0.6  # Approximate character width
                text_width = len(test_line) * char_width
                
                if text_width < (page_width - 2 * margin):
                    current_line = test_line
                else:
                    # Print current line and start new one
                    if current_line:
                        if y_position < margin:  # Start new page if needed
                            break
                        page.insert_text(
                            (margin, y_position), 
                            current_line, 
                            fontsize=current_font_size
                        )
                        y_position -= line_height
                    current_line = word
            
            # Print the last line
            if current_line and y_position >= margin:
                page.insert_text(
                    (margin, y_position), 
                    current_line, 
                    fontsize=current_font_size
                )
                y_position -= line_height * 1.2  # Extra space after paragraphs

    def _setup_openai_client(self) -> openai.OpenAI:
        """Setup OpenAI client with Copilot token."""
        token = get_access_token_from_copilot()
        return openai.OpenAI(
            api_key=token,
            base_url=config.LLM_BASE_URL,
            default_headers={
                "editor-version": "vscode/1.104.0",
                "editor-plugin-verion": "copilot.vim/1.16.0",
                "user-agent": "GithubCopilot/1.155.0",
            },
        )

    def _detect_file_type(self, file_path: str) -> FileType:
        """Detect file type from file path or URL."""
        path_lower = file_path.lower()

        if "adobe.com" in path_lower or "express.adobe.com" in path_lower:
            return FileType.ADOBE_EXPRESS
        elif path_lower.endswith(".pdf"):
            return FileType.PDF
        elif path_lower.endswith(".docx"):
            return FileType.DOCX
        elif path_lower.endswith((".txt", ".md")):
            return FileType.TEXT
        else:
            raise ValueError(f"Unsupported file type for: {file_path}")

    def _create_enhancement_prompt(
        self,
        cv_content: str,
        job_description: str,
        additional_input: Optional[Union[str, Dict]] = None,
    ) -> str:
        """Create comprehensive prompt for CV enhancement."""

        additional_context = ""
        if additional_input:
            if isinstance(additional_input, str):
                additional_context = f"\n\nAdditional Context:\n{additional_input}"
            elif isinstance(additional_input, dict):
                additional_context = (
                    f"\n\nAdditional Context:\n{json.dumps(additional_input, indent=2)}"
                )

        return f"""You are an expert CV enhancement specialist. Transform the provided CV to align with the job description while maintaining authenticity.

## Enhancement Requirements:

### 1. Header & Name Formatting
- Start with the candidate's name as the MAIN HEADER (use # in markdown). First Name and Middle Initial only (Satadeep Dasgupta -> S Dasgupta).
- Follow with job title/role (use ## in markdown)
- Do NOT include any contact information, addresses, emails, or phone numbers
- Keep the header clean and professional

### 2. JD Alignment & Content Refinement
- Analyze job requirements and optimize CV content accordingly
- Add missing elements that align with job requirements (realistically)
- Optimize keywords for ATS compatibility
- Enhance achievements with quantifiable results

### 3. Anonymization
- Remove ALL company names - replace with generic descriptions (e.g., "Leading Tech Company")
- Remove ALL personal contact details (email, phone, address)
- Maintain role context without revealing specific organizations

### 4. Portfolio & Project Enhancement
- Expand project descriptions with technical details
- Add relevant tech stacks and methodologies
- Include project scope and business impact with metrics
- Add modern technologies that align with the JD (realistically)

### 5. Content Restrictions
- Do NOT include "Portfolio, code samples, and certification transcripts available upon request"
- Do NOT include any availability statements or contact requests
- Do NOT include any meta-commentary about the enhancement process
- Do NOT mention that "this CV was enhanced" or reference the enhancement process
- Focus only on professional qualifications and achievements

## Current CV:
{cv_content}

## Job Description:
{job_description}
{additional_context}

Return ONLY the enhanced CV content starting with the candidate's name as the main header, followed by sections: Professional Summary, Technical Skills, Professional Experience, Projects, Education. Use proper markdown formatting with # for the name and ## for section headers. Do not include any commentary or explanations about the enhancement process."""

    def process_cv_enhancement(
        self,
        cv_file_path: str,
        job_description: str,
        additional_input: Optional[Union[str, Dict]] = None,
        output_path: str = "resume.html",
        generate_pdf: bool = True,
        include_logo: bool = True,
    ) -> str:
        """
        Process CV enhancement using LangGraph workflow.

        Args:
            cv_file_path: Path to CV file or Adobe Express URL
            job_description: Job description for alignment
            additional_input: Optional additional context
            output_path: Output path for enhanced resume

        Returns:
            Path to generated enhanced resume file
        """
        logger.info(f"Starting CV enhancement workflow for: {cv_file_path}")

        # Initialize state
        initial_state: CVState = {
            "file_path": cv_file_path,
            "job_description": job_description,
            "additional_input": additional_input,
            "cv_content": "",
            "enhanced_content": "",
            "output_path": output_path,
            "generate_pdf": generate_pdf,
            "include_logo": include_logo,
        }

        # Run workflow
        self.workflow.invoke(initial_state)

        logger.info(f"CV enhancement workflow completed: {output_path}")
        return str(Path(output_path).absolute())


def create_cv_enhancement_agent() -> CVEnhancementAgent:
    """Factory function to create CV enhancement agent."""
    return CVEnhancementAgent()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    agent = create_cv_enhancement_agent()

    job_desc = """
    Senior Software Engineer - Full Stack Development
    
    Required Skills:
    - 5+ years of software development experience
    - Proficiency in Python, JavaScript, React, Node.js
    - Experience with cloud platforms (AWS, Azure)
    - Knowledge of databases (PostgreSQL, MongoDB)
    - Experience with microservices architecture
    """

    try:
        print("CV Enhancement Agent (LangGraph) initialized successfully!")
        print("Use agent.process_cv_enhancement() to enhance CVs")

    except Exception as e:
        logger.error(f"Example execution failed: {e}")
