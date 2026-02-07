"""
Dynamic Resume Generator - Streamlit UI (Frontend)

Connects to the FastAPI backend to generate resumes.
"""

import streamlit as st
import requests

# API Configuration
API_URL = "http://localhost:8000"

# --- Constants for UI ---
PROVIDERS = {
    "OpenAI": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    "Anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
    "Google Gemini": ["gemini-pro", "gemini-1.5-pro-latest"],
    "Groq": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"],
    "Ollama": ["llama3", "mistral", "gemma:7b"]
}

# Page configuration
st.set_page_config(
    page_title="Dynamic Resume Creator",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stTextArea textarea { font-family: monospace; font-size: 12px; }
    .success-box { padding: 1rem; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)


def get_ollama_models():
    """Fetch available models from local Ollama instance."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = [model["name"] for model in response.json().get("models", [])]
            return models
    except Exception:
        pass
    return ["llama3", "mistral", "gemma:7b"]  # Fallback


def render_sidebar():
    st.sidebar.header("🤖 Model Settings")

    # Map display name to internal ID
    provider_map = {
        "OpenAI": "openai",
        "Anthropic": "anthropic",
        "Google Gemini": "gemini",
        "Groq": "groq",
        "Ollama": "ollama"
    }

    # Advanced mode toggle
    advanced_mode = st.sidebar.checkbox("🔧 Advanced: Individual Models per Agent", value=False)

    if not advanced_mode:
        # Simple mode: one model for all agents
        st.sidebar.subheader("Unified Model")
        provider_display = st.sidebar.selectbox("Provider", list(PROVIDERS.keys()), key="unified_provider")
        provider_id = provider_map[provider_display]

        if provider_display == "Ollama":
            available_models = get_ollama_models()
        else:
            available_models = PROVIDERS[provider_display]

        model = st.sidebar.selectbox("Model", available_models, key="unified_model")

        api_key = None
        if provider_id != "ollama":
            api_key = st.sidebar.text_input(f"{provider_display} API Key", type="password", key="unified_key")

        return {
            "mode": "simple",
            "unified": {
                "provider": provider_id,
                "model": model,
                "api_key": api_key
            }
        }
    else:
        # Advanced mode: individual models for each agent
        configs = {}

        for agent_name in ["Analyzer", "Strategist", "Developer"]:
            st.sidebar.markdown(f"**{agent_name} Agent**")

            provider_display = st.sidebar.selectbox(
                "Provider",
                list(PROVIDERS.keys()),
                key=f"{agent_name}_provider"
            )
            provider_id = provider_map[provider_display]

            if provider_display == "Ollama":
                available_models = get_ollama_models()
            else:
                available_models = PROVIDERS[provider_display]

            model = st.sidebar.selectbox(
                "Model",
                available_models,
                key=f"{agent_name}_model"
            )

            api_key = None
            if provider_id != "ollama":
                api_key = st.sidebar.text_input(
                    "API Key",
                    type="password",
                    key=f"{agent_name}_key"
                )

            configs[agent_name.lower()] = {
                "provider": provider_id,
                "model": model,
                "api_key": api_key
            }

            if agent_name != "Developer":  # Don't add divider after last agent
                st.sidebar.divider()

        return {
            "mode": "advanced",
            "configs": configs
        }


def main():
    st.title("📄 Dynamic Resume Creator (Agentic)")

    # Check Backend Health
    try:
        requests.get(f"{API_URL}/health", timeout=1)
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend API is not running. Please run `uvicorn app_server:app --reload` in a terminal.")
        st.stop()

    model_config = render_sidebar()

    # --- Inputs ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Job Description")
        job_desc = st.text_area("Paste the job description here...", height=200)

    with col2:
        st.subheader("2. Your Experience")
        experience = st.text_area("Paste your raw experience/CV content...", height=200)

    st.subheader("3. Sample LaTeX (Template)")
    sample_latex = st.text_area("Paste a working LaTeX template...", height=300,
                                value="\\documentclass{article}\n\\begin{document}\n% content\n\\end{document}")

    # --- Generation ---
    if st.button("🚀 Generate Resume", type="primary"):
        if not job_desc or not experience:
            st.warning("Please provide both Job Description and Experience.")
            return

        with st.spinner("Agents are working... (Analyzing -> Strategizing -> Writing -> Compiling)"):
            # Build payload based on mode
            payload = {
                "job_description": job_desc,
                "raw_experience": experience,
                "sample_latex": sample_latex,
            }

            if model_config["mode"] == "simple":
                # Legacy single model config
                payload.update({
                    "provider": model_config["unified"]["provider"],
                    "model": model_config["unified"]["model"],
                    "api_key": model_config["unified"]["api_key"]
                })
            else:
                # Advanced mode: individual configs
                payload.update({
                    "analyzer_config": model_config["configs"]["analyzer"],
                    "strategist_config": model_config["configs"]["strategist"],
                    "developer_config": model_config["configs"]["developer"]
                })

            try:
                # Increased timeout to 300s for agentic workflows
                response = requests.post(f"{API_URL}/generate", json=payload, timeout=300)

                if response.status_code == 200:
                    data = response.json()

                    # Display Results
                    st.success(f"Generation Complete! (Revisions: {data['revision_count']})")

                    with st.expander("📊 Analysis & Strategy"):
                        st.subheader("Job Analysis")
                        st.markdown(data['analysis'])
                        st.divider()
                        st.subheader("Strategy Plan")
                        st.markdown(data['strategy'])

                    with st.expander("🚨 Compilation Report", expanded=not data['is_valid']):
                        if data['is_valid']:
                            st.success("LaTeX is valid (No syntax errors found).")
                        else:
                            st.error(f"Found Errors: {data['errors']}")

                    st.subheader("📝 Final LaTeX")
                    st.code(data['final_latex'], language="latex")
                    st.download_button("Download .tex", data['final_latex'], "resume.tex")

                else:
                    st.error(f"Server Error: {response.text}")

            except Exception as e:
                st.error(f"Client Error: {str(e)}")


if __name__ == "__main__":
    main()
