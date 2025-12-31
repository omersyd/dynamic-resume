"""
Dynamic Resume Generator - Streamlit UI

A tool to generate tailored LaTeX resumes based on job descriptions.
"""

import streamlit as st
from core.resume_generator import ResumeGenerator, create_provider
from core.prompts import CREATIVITY_LEVELS
from providers import PROVIDERS, PROVIDER_MODELS


# Page configuration
st.set_page_config(
    page_title="Dynamic Resume Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stTextArea textarea {
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 12px;
    }
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .stAlert {
        padding: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'generated_latex' not in st.session_state:
        st.session_state.generated_latex = ""
    if 'generation_complete' not in st.session_state:
        st.session_state.generation_complete = False


def render_sidebar():
    """Render the sidebar with LLM settings."""
    st.sidebar.header("🤖 LLM Settings")

    # Provider selection
    provider = st.sidebar.selectbox(
        "Provider",
        options=list(PROVIDERS.keys()),
        help="Select the LLM provider to use for generation"
    )

    # API Key input (not needed for Ollama)
    api_key = None
    ollama_endpoint = "http://localhost:11434"
    available_models = PROVIDER_MODELS.get(provider, [])

    if provider == "Ollama":
        st.sidebar.info("🦙 Ollama runs locally - no API key needed!")
        ollama_endpoint = st.sidebar.text_input(
            "Ollama Endpoint",
            value="http://localhost:11434",
            help="The endpoint where Ollama is running"
        )
        # Check if Ollama is running and get available models
        try:
            from providers.ollama_provider import OllamaProvider
            ollama = OllamaProvider(endpoint=ollama_endpoint)
            if ollama.validate_connection():
                st.sidebar.success("✅ Ollama is running")
                local_models = ollama.list_available_models()
                if local_models:
                    # Use dynamically detected models instead of static list
                    available_models = local_models
                else:
                    st.sidebar.caption("No models found. Pull one with: ollama pull llama3.2")
            else:
                st.sidebar.warning("⚠️ Ollama not detected. Make sure it's running.")
        except Exception:
            st.sidebar.warning("⚠️ Could not connect to Ollama")
    else:
        # Non-Ollama providers need API key
        api_key = st.sidebar.text_input(
            "API Key",
            type="password",
            help=f"Enter your {provider} API key. It's only stored in memory for this session."
        )

        # Show where to get API key
        api_key_links = {
            "OpenAI": "https://platform.openai.com/api-keys",
            "Anthropic": "https://console.anthropic.com/settings/keys",
            "Groq": "https://console.groq.com/keys",
            "Google Gemini": "https://aistudio.google.com/app/apikey",
        }
        if provider in api_key_links:
            st.sidebar.caption(f"[Get {provider} API Key]({api_key_links[provider]})")

    # Model selection based on provider (moved after Ollama detection)
    model = st.sidebar.selectbox(
        "Model",
        options=available_models if available_models else ["No models available"],
        help="Select the specific model to use"
    )

    st.sidebar.divider()

    # Creativity level
    st.sidebar.header("🎨 Generation Settings")

    creativity_level = st.sidebar.slider(
        "Creativity Level",
        min_value=1,
        max_value=5,
        value=3,
        help="How much creative liberty should the AI take?"
    )

    # Show creativity level description
    level_info = CREATIVITY_LEVELS[creativity_level]
    st.sidebar.info(f"**{level_info['name']}**: {level_info['description']}")

    return {
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "ollama_endpoint": ollama_endpoint,
        "creativity_level": creativity_level,
    }


def render_main_content(settings):
    """Render the main content area."""

    # Header
    st.markdown("<h1 class='main-header'>📄 Dynamic Resume Generator</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #666;'>"
        "Generate tailored LaTeX resumes that match job descriptions</p>",
        unsafe_allow_html=True
    )

    st.divider()

    # Input section with three columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📝 Sample LaTeX Resume")
        st.caption("Paste your existing LaTeX resume to define the style")
        sample_latex = st.text_area(
            "Sample LaTeX",
            height=400,
            placeholder="\\documentclass{article}\n\\begin{document}\n...\n\\end{document}",
            label_visibility="collapsed"
        )

    with col2:
        st.subheader("💼 Your Experience")
        st.caption("Paste your full experience, skills, projects, education")
        experience = st.text_area(
            "Experience",
            height=400,
            placeholder=(
                "Work Experience:\n- Company A (2020-2023)\n  - Built scalable systems...\n\n"
                "Skills:\n- Python, JavaScript...\n\nEducation:\n- BS Computer Science..."
            ),
            label_visibility="collapsed"
        )

    with col3:
        st.subheader("🎯 Job Description")
        st.caption("Paste the target job description")
        job_description = st.text_area(
            "Job Description",
            height=400,
            placeholder=(
                "We are looking for a Senior Software Engineer...\n\nRequirements:\n"
                "- 5+ years of experience...\n- Strong Python skills..."
            ),
            label_visibility="collapsed"
        )

    # Custom instructions (collapsible)
    with st.expander("✨ Custom Instructions (Optional)"):
        custom_instructions = st.text_area(
            "Additional instructions for the AI",
            height=100,
            placeholder="Focus on leadership experience, emphasize Python and cloud skills, keep it to one page...",
            label_visibility="collapsed"
        )

    if 'custom_instructions' not in locals():
        custom_instructions = ""

    st.divider()

    # Generate button
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        generate_clicked = st.button(
            "🚀 Generate Resume",
            type="primary",
            use_container_width=True
        )

    # Validation and generation
    if generate_clicked:
        # Validate inputs
        errors = []
        if not sample_latex.strip():
            errors.append("Please provide a sample LaTeX resume")
        if not experience.strip():
            errors.append("Please provide your experience")
        if not job_description.strip():
            errors.append("Please provide a job description")
        if settings["provider"] != "Ollama" and not settings["api_key"]:
            errors.append(f"Please enter your {settings['provider']} API key in the sidebar")

        if errors:
            for error in errors:
                st.error(error)
        else:
            # Generate resume
            try:
                with st.spinner("🔄 Generating your tailored resume... This may take a minute."):
                    # Create provider
                    provider = create_provider(
                        provider_name=settings["provider"],
                        api_key=settings["api_key"],
                        model=settings["model"],
                        ollama_endpoint=settings["ollama_endpoint"]
                    )

                    # Create generator and generate
                    generator = ResumeGenerator(provider)
                    generated_latex = generator.generate(
                        sample_latex=sample_latex,
                        experience=experience,
                        job_description=job_description,
                        creativity_level=settings["creativity_level"],
                        custom_instructions=custom_instructions
                    )

                    st.session_state.generated_latex = generated_latex
                    st.session_state.generation_complete = True

            except Exception as e:
                st.error(f"❌ Generation failed: {str(e)}")
                st.session_state.generation_complete = False

    # Output section
    if st.session_state.generation_complete and st.session_state.generated_latex:
        st.divider()
        st.subheader("✅ Generated Resume")

        # Success message
        st.success(
            "Resume generated successfully! Copy the LaTeX below and paste it into "
            "Overleaf or your LaTeX editor."
        )

        # Output text area
        st.text_area(
            "Generated LaTeX",
            value=st.session_state.generated_latex,
            height=500,
            label_visibility="collapsed"
        )

        # Copy button and download
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.download_button(
                label="📥 Download .tex file",
                data=st.session_state.generated_latex,
                file_name="tailored_resume.tex",
                mime="text/plain"
            )
        with col2:
            # Note: Streamlit doesn't have native clipboard support,
            # but the text area itself allows easy selection and copy
            st.info("💡 Tip: Triple-click in the text area to select all, then Cmd+C to copy")


def main():
    """Main application entry point."""
    init_session_state()
    settings = render_sidebar()
    render_main_content(settings)

    # Footer
    st.sidebar.divider()
    st.sidebar.caption("Built with ❤️ using Streamlit")
    st.sidebar.caption("Your API keys are never stored - session only!")


if __name__ == "__main__":
    main()
