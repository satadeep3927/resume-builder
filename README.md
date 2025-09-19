# CV Enhancement Agent

A comprehensive AI-powered agent for enhancing CVs and resumes with job description alignment, anonymization, and professional PDF formatting with Brainium branding.

## 🎯 Features

### Core Enhancement Capabilities
- **JD Alignment**: Refines CV content to match job description requirements
- **Anonymization**: Removes company names and contact details while maintaining context
- **Portfolio Enhancement**: Expands project descriptions with technical depth
- **PDF Generation**: Creates professional PDFs with Brainium logo
- **Web Interface**: Easy-to-use Streamlit app

### Supported Input Formats
- PDF documents (`.pdf`)
- Word documents (`.docx`)
- Adobe Express URLs (published documents)

### AI-Powered Enhancements
- Uses GPT-4.1 via GitHub Copilot API
- Intelligent content refinement and expansion
- Technical skill enhancement and modernization
- Achievement quantification and impact highlighting

## 🚀 Quick Start

### 1. Installation & Setup

```bash
# Clone/download the project
cd resume-builder

# Easy setup with launcher
python launch.py
```

**OR Manual setup:**

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.template .env
# Edit .env and add your COPILOT_ACCESS_TOKEN

# Launch Streamlit app
streamlit run streamlit_app.py
```

### 2. Environment Configuration

Create `.env` file:
```bash
COPILOT_ACCESS_TOKEN=your_github_copilot_token_here
```

### 3. Using the Web App

1. **Open** http://localhost:8501 in your browser
2. **Upload** CV file (PDF/DOCX) OR paste Adobe Express URL
3. **Enter** target job description
4. **Configure** advanced options (optional)
5. **Click** "Enhance CV" 
6. **Download** generated PDF with Brainium logo

## 📱 Streamlit Web Interface

### Main Features
- **File Upload**: Drag & drop PDF/DOCX files
- **Adobe Express**: Direct URL input for published documents
- **Job Description**: Large text area with examples
- **Advanced Config**: Collapsible section with:
  - Focus areas (Frontend, Backend, DevOps, etc.)
  - Enhancement preferences
  - Target company type
- **PDF Generation**: Professional output with logo
- **Live Preview**: HTML preview before download

### Interface Sections
```
┌─────────────────────────────────────┐
│          🏢 Brainium Logo           │
│      CV Enhancement Agent           │
├─────────────────┬───────────────────┤
│  📄 CV Input    │  🎯 Job Description│
│  • Upload File  │  • Text area      │
│  • Adobe URL    │  • Examples       │
│                 │  • Custom instruct│
├─────────────────┴───────────────────┤
│          🚀 Enhance CV              │
├─────────────────────────────────────┤
│          📥 Download Results        │
│      📄 PDF    |    🌐 HTML         │
└─────────────────────────────────────┘
```

## � API Reference

### CVEnhancementAgent (LangGraph)

Enhanced with LangGraph workflow:

```python
from agents.cv_enhancement_agent import create_cv_enhancement_agent

agent = create_cv_enhancement_agent()

result = agent.process_cv_enhancement(
    cv_file_path="resume.pdf",          # File path or Adobe URL
    job_description="Job requirements...",
    additional_input={"focus_areas": ["backend"]},
    output_path="enhanced_resume",      # Without extension
    generate_pdf=True                   # PDF with logo
)
```

### Workflow Nodes
1. **load_document** → Extract content from PDF/DOCX/Adobe Express
2. **enhance_content** → AI enhancement with GPT-4.1
3. **generate_output** → Create HTML/PDF with Brainium logo

## 🎨 Output Formats

### PDF Features
- **Professional Layout**: Clean, ATS-friendly design
- **Brainium Logo**: Prominently displayed at top
- **Responsive Design**: Optimized for printing and digital viewing
- **Styled Sections**: Consistent formatting and typography

### Template Structure
```html
<!DOCTYPE html>
<html>
<head>
    <style>/* Professional CSS styling */</style>
</head>
<body>
    <div class="header">
        <img src="brainium-logo.svg" class="logo">
    </div>
    <div class="content">
        {{ enhanced_cv_content }}
    </div>
</body>
</html>
```

## ⚙️ Configuration Options

### Advanced Settings (Web UI)
- **Focus Areas**: Frontend, Backend, Full Stack, DevOps, Cloud, AI/ML
- **Enhancement Preferences**:
  - Add leadership experience
  - Emphasize scalability
  - Include performance metrics
- **Target Company**: Startup, Enterprise, Consulting, etc.

### Additional Input Formats
```python
# String format
additional_input = "Focus on cloud architecture and microservices"

# Structured format
additional_input = {
    "focus_areas": ["backend", "cloud"],
    "enhancement_preferences": {
        "add_leadership_experience": True,
        "emphasize_scalability": True,
        "include_metrics": True
    },
    "target_company_type": "Enterprise"
}
```

## 🛠️ Technical Stack

- **Backend**: LangGraph + OpenAI GPT-4.1
- **Document Processing**: LangChain (PDF, DOCX, Adobe Express)
- **PDF Generation**: WeasyPrint
- **Web Interface**: Streamlit
- **Templates**: Jinja2
- **Authentication**: GitHub Copilot API

## 📁 Project Structure

```
resume-builder/
├── streamlit_app.py              # Web interface
├── launch.py                     # Easy launcher script
├── agents/
│   └── cv_enhancement_agent.py   # LangGraph agent
├── core/
│   ├── document_loader.py        # Document loading
│   └── loaders/
│       └── adobe_express_loader.py
├── templates/
│   └── resume_template.md        # HTML template with logo
├── assets/
│   └── brainium-logo.svg        # Company branding
├── .env.template                 # Environment setup
└── requirements.txt              # Dependencies
```

## � Requirements

- Python 3.8+
- GitHub Copilot access token
- WeasyPrint (for PDF generation)
- Streamlit (for web interface)

## 🎯 Usage Examples

### Web App Usage
1. **Upload CV**: `my_resume.pdf`
2. **Job Description**: 
   ```
   Senior Full Stack Developer
   Requirements: Python, React, AWS, 5+ years experience
   ```
3. **Advanced Config**: Focus on "Full Stack" + "Cloud"
4. **Result**: Professional PDF with Brainium logo

### Programmatic Usage
```python
agent = create_cv_enhancement_agent()

# Process with Adobe Express URL
result = agent.process_cv_enhancement(
    cv_file_path="https://new.express.adobe.com/publishedV2/...",
    job_description="Senior Developer role requiring...",
    generate_pdf=True
)
```

## 🚀 Deployment

### Local Development
```bash
python launch.py
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export COPILOT_ACCESS_TOKEN=your_token

# Run with custom port
streamlit run streamlit_app.py --server.port 8080
```

## 💡 Tips & Best Practices

1. **Job Descriptions**: More detailed JDs = better alignment
2. **File Formats**: PDF generally works better than DOCX
3. **Adobe Express**: Use published/public document URLs
4. **Focus Areas**: Select 2-3 relevant areas for best results
5. **Custom Instructions**: Be specific about requirements

## 🆘 Troubleshooting

### Common Issues
- **WeasyPrint errors**: Install system dependencies
- **Adobe Express 403**: URL might not be publicly accessible  
- **Token errors**: Check COPILOT_ACCESS_TOKEN in .env
- **PDF generation fails**: Falls back to HTML automatically

### Support
Run the test script to verify setup:
```bash
python test_cv_agent.py
```

## 📄 License

MIT License - See LICENSE file for details.