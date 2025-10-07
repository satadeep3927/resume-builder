"""
Streamlit App for CV Enhancement Agent

This app provides a web interface for enhancing CVs with:
- File upload (PDF, DOCX) or Adobe Express URL input
- Job description input
- Advanced configuration options
- PDF output with Brainium logo
"""

import logging
import os
import tempfile
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from agents.cv_enhancement_agent import create_cv_enhancement_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_files(file_paths):
    """Clean up generated files after download."""
    import time
    import threading
    
    def delayed_cleanup():
        # Wait a bit to ensure download completes
        time.sleep(2)
        for file_path in file_paths:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not clean up {file_path}: {e}")
    
    # Run cleanup in background thread
    threading.Thread(target=delayed_cleanup, daemon=True).start()

# Page config
st.set_page_config(
    page_title="CV Enhancement Agent",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f0f0;
        margin-bottom: 2rem;
    }
    .logo {
        max-width: 200px;
        height: auto;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    """Main Streamlit app."""

    # Header with logo
    st.markdown('<div class="main-header">', unsafe_allow_html=True)

    # Display logo if exists
    logo_path = Path("assets/brainium-logo.svg")
    if logo_path.exists():
        st.image(str(logo_path), width=200)

    st.title("🚀 CV Enhancement Agent")
    st.markdown("*Transform your CV with AI-powered optimization*")
    st.markdown("</div>", unsafe_allow_html=True)

    # Initialize session state
    if "processed" not in st.session_state:
        st.session_state.processed = False
    if "result_path" not in st.session_state:
        st.session_state.result_path = None
    if "edited_content" not in st.session_state:
        st.session_state.edited_content = ""

    # Sidebar for advanced options
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Output format
        generate_pdf = st.checkbox(
            "Generate PDF", value=True, help="Generate PDF output"
        )

        # Logo option
        include_logo = st.checkbox(
            "Include Brainium Logo",
            value=True,
            help="Add Brainium logo to the generated resume",
        )

        # Advanced options in expander
        with st.expander("🔧 Advanced Options"):
            focus_areas = st.multiselect(
                "Focus Areas",
                [
                    "Frontend",
                    "Backend",
                    "Full Stack",
                    "DevOps",
                    "Cloud",
                    "AI/ML",
                    "Mobile",
                    "Data",
                ],
                help="Specific areas to emphasize in enhancement",
            )

            add_leadership = st.checkbox(
                "Add Leadership Experience", help="Enhance with leadership examples"
            )
            emphasize_scale = st.checkbox(
                "Emphasize Scalability", help="Highlight scalable solutions"
            )
            include_metrics = st.checkbox("Include Performance Metrics", value=True)

            target_company = st.selectbox(
                "Target Company Type",
                [
                    "Startup",
                    "Enterprise",
                    "Consulting",
                    "Product Company",
                    "Service Company",
                ],
                help="Tailor content for specific company type",
            )

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📄 CV Input")

        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Upload File", "Adobe Express URL"],
            horizontal=True,
        )

        cv_file_path = None

        if input_method == "Upload File":
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Upload your CV",
                type=["pdf", "docx"],
                help="Supported formats: PDF, DOCX",
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if uploaded_file is not None:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}"
                ) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    cv_file_path = tmp_file.name

                st.success(f"✅ Uploaded: {uploaded_file.name}")

        else:  # Adobe Express URL
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            adobe_url = st.text_input(
                "Adobe Express URL",
                placeholder="https://new.express.adobe.com/publishedV2/urn:aaid:sc:AP:...",
                help="Paste your Adobe Express published document URL",
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if adobe_url and adobe_url.startswith("https://"):
                cv_file_path = adobe_url
                st.success("✅ Adobe Express URL provided")

    with col2:
        st.subheader("🎯 Job Description")

        job_description = st.text_area(
            "Target Job Description",
            height=300,
            key="job_description_input",
            placeholder="""Enter the job description you want to align your CV with...

Example:
Senior Software Engineer - Full Stack

Requirements:
• 5+ years of software development
• Python, JavaScript, React, Node.js
• Cloud platforms (AWS, Azure)
• Database experience (PostgreSQL, MongoDB)
• Microservices architecture
""",
            help="The more detailed the job description, the better the alignment",
        )

        # Collapsible advanced input
        with st.expander("📋 Additional Instructions (Optional)"):
            additional_text = st.text_area(
                "Custom Instructions",
                height=150,
                placeholder="Add specific instructions for enhancement...\n\nExample:\n- Focus on backend development\n- Emphasize leadership skills\n- Include startup experience",
                help="Provide specific guidance for the enhancement process",
            )

    # Process button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_btn = st.button(
            "🚀 Enhance CV",
            type="primary",
            use_container_width=True,
        )

    # Processing - validate inputs when button is clicked
    if process_btn:
        # Validate inputs
        if not cv_file_path:
            st.error("❌ Please provide a CV file or Adobe Express URL")
        elif not job_description or not job_description.strip():
            st.error("❌ Please provide a job description")
        else:
            # Inputs are valid, proceed with processing
            # Prepare additional input
            additional_input = {}
            if focus_areas:
                additional_input["focus_areas"] = focus_areas
            if additional_text.strip():
                additional_input["custom_instructions"] = additional_text

            additional_input.update(
                {
                    "enhancement_preferences": {
                        "add_leadership_experience": add_leadership,
                        "emphasize_scalability": emphasize_scale,
                        "include_metrics": include_metrics,
                    },
                    "target_company_type": target_company,
                }
            )

            with st.spinner("🔄 Enhancing your CV... This may take a few moments."):
                try:
                    # Create agent and process
                    agent = create_cv_enhancement_agent()

                    output_path = "enhanced_resume"
                    result_path = agent.process_cv_enhancement(
                        cv_file_path=cv_file_path,
                        job_description=job_description,
                        additional_input=additional_input,
                        output_path=output_path,
                        generate_pdf=generate_pdf,
                        include_logo=include_logo,
                    )

                    st.session_state.processed = True
                    st.session_state.result_path = result_path
                    # Clear edited content so new enhancement will be loaded
                    st.session_state.edited_content = ""

                    st.success("✅ CV Enhancement completed successfully!")

                    # Clean up temporary file
                    if (
                        input_method == "Upload File"
                        and cv_file_path
                        and os.path.exists(cv_file_path)
                    ):
                        os.unlink(cv_file_path)

                except Exception as e:
                    st.error(f"❌ Enhancement failed: {str(e)}")
                    logger.error(f"Enhancement error: {e}")

    # Display results
    if st.session_state.processed and st.session_state.result_path:
        st.markdown("---")
        st.subheader("� Review & Edit Results")

        result_path = Path(st.session_state.result_path)
        html_file = result_path.with_suffix(".html")
        pdf_file = result_path.with_suffix(".pdf")

        # Load the enhanced content for editing - ONLY ONCE when first processing
        if html_file.exists() and not st.session_state.edited_content:
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
                
            # Extract enhanced content from HTML
            import re
            
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                content_div = soup.find('div', class_='content')
                
                if content_div:
                    # Convert HTML back to markdown-like text for editing
                    enhanced_text = content_div.get_text(separator='\n\n', strip=True)
                else:
                    # Fallback - try to extract from HTML structure
                    enhanced_text = "Could not extract content for editing. Please regenerate."
            except ImportError:
                # If BeautifulSoup is not available, use regex fallback
                content_match = re.search(r'<div class="content">\s*(.*?)\s*</div>', html_content, re.DOTALL | re.IGNORECASE)
                if content_match:
                    enhanced_text = content_match.group(1).strip()
                    # Basic HTML tag removal
                    enhanced_text = re.sub(r'<[^>]+>', '', enhanced_text)
                else:
                    enhanced_text = "Could not extract content for editing. Please regenerate."

            # Set the content ONLY if it's empty
            st.session_state.edited_content = enhanced_text

        # ALWAYS show tabs for Edit and Preview (moved outside the if condition)
        edit_tab, preview_tab = st.tabs(["✏️ Edit Content", "👀 Preview"])
        
        with edit_tab:
            st.markdown("**Edit your enhanced CV content below:**")
            
            # Editable text area - ALWAYS use session state as source of truth
            edited_content = st.text_area(
                "Enhanced CV Content",
                value=st.session_state.edited_content,
                height=500,
                key="cv_editor",
                help="You can edit the enhanced CV content here. The formatting will be preserved when regenerating the PDF.",
            )
            
            # ALWAYS update session state when content changes
            st.session_state.edited_content = edited_content
            
            # Regenerate button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Regenerate PDF with Changes", type="primary", use_container_width=True):
                    with st.spinner("🔄 Regenerating PDF with your changes..."):
                        try:
                            # Create agent
                            agent = create_cv_enhancement_agent()
                            
                            # Generate new files with edited content - use CURRENT content from text area
                            new_output_path = f"edited_resume_{int(time.time())}"
                            
                            # Call the agent's method to generate PDF with custom content
                            success = agent._generate_pdf_from_content(
                                content=edited_content,  # Use the content from the text area directly
                                output_path=new_output_path,
                                include_logo=include_logo
                            )
                            
                            if success:
                                # Update session state with new files
                                st.session_state.result_path = new_output_path
                                st.success("✅ PDF regenerated successfully with your changes!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to regenerate PDF")
                                
                        except Exception as e:
                            st.error(f"❌ Regeneration failed: {str(e)}")
                            logger.error(f"Regeneration error: {e}")
        
        with preview_tab:
            st.markdown("**Preview of your edited content:**")
            
            # Display the edited content as markdown
            if st.session_state.edited_content:
                st.markdown(st.session_state.edited_content)
            else:
                st.info("No content to preview. Please edit the content in the Edit tab.")

        # Download section
        st.markdown("---")
        st.subheader("📥 Download Files")

        col1, col2 = st.columns(2)

        with col1:
            if pdf_file.exists():
                with open(pdf_file, "rb") as f:
                    pdf_data = f.read()
                    st.download_button(
                        "📄 Download PDF",
                        data=pdf_data,
                        file_name=f"enhanced_resume_{int(time.time())}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        on_click=lambda: cleanup_files([pdf_file, html_file]),
                    )

        with col2:
            if html_file.exists():
                with open(html_file, "r", encoding="utf-8") as f:
                    html_data = f.read()
                    st.download_button(
                        "🌐 Download HTML",
                        data=html_data,
                        file_name=f"enhanced_resume_{int(time.time())}.html",
                        mime="text/html",
                        use_container_width=True,
                        on_click=lambda: cleanup_files([pdf_file, html_file]),
                    )

        # Additional feature: Save as different format
        st.markdown("---")
        with st.expander("� Additional Download Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Download as plain text
                if st.session_state.edited_content:
                    st.download_button(
                        "📝 Download as Text (.txt)",
                        data=st.session_state.edited_content,
                        file_name=f"enhanced_resume_{int(time.time())}.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
            
            with col2:
                # Download as markdown
                if st.session_state.edited_content:
                    st.download_button(
                        "📋 Download as Markdown (.md)",
                        data=st.session_state.edited_content,
                        file_name=f"enhanced_resume_{int(time.time())}.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
        "CV Enhancement Agent • Powered by AI • Built with ❤️"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
