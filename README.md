# 📄 Dynamic Resume Generator

A tool that generates tailored LaTeX resumes based on a sample resume, your experience, and a target job description.

## ✨ Features

- **Pluggable LLM Providers**: Switch between OpenAI, Anthropic, Groq, Google Gemini, or Ollama (local)
- **Creativity Levels**: Control how much the AI adapts your resume (Conservative → Bold)
- **LaTeX Output**: Generates valid LaTeX that compiles directly in Overleaf
- **Custom Instructions**: Fine-tune the generation with your own instructions
- **Session-only API Keys**: Your credentials are never stored

## 🚀 Quick Start

### 1. Clone and setup

```bash
cd dynamic-resume-creator
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

### 3. Open in browser

The app will open automatically at `http://localhost:8501`

## 🤖 Supported LLM Providers

| Provider | Cost | Setup |
|----------|------|-------|
| **OpenAI** | Paid | [Get API Key](https://platform.openai.com/api-keys) |
| **Anthropic** | Paid | [Get API Key](https://console.anthropic.com/settings/keys) |
| **Groq** | Free tier | [Get API Key](https://console.groq.com/keys) |
| **Google Gemini** | Free tier | [Get API Key](https://aistudio.google.com/app/apikey) |
| **Ollama** | Free (local) | [Install Ollama](https://ollama.ai) |

### Using Ollama (Free & Private)

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a model: `ollama pull llama3.3`
3. Run Ollama: `ollama serve`
4. Select "Ollama" in the app sidebar

## 📖 How to Use

1. **Paste your sample LaTeX resume** - This defines the style and structure
2. **Paste your full experience** - Include all jobs, skills, projects, education
3. **Paste the job description** - The target role you're applying for
4. **Adjust creativity level** - How much should the AI adapt your content?
5. **Click Generate** - Get your tailored LaTeX resume
6. **Copy to Overleaf** - Compile and download your PDF

## 🎨 Creativity Levels

| Level | Name | Behavior |
|-------|------|----------|
| 1 | Conservative | Minimal changes, mostly reorganization |
| 2 | Moderate | Light rewording, adds keywords |
| 3 | Balanced | Active tailoring while staying truthful |
| 4 | Creative | Significant rewriting, highlights transferable skills |
| 5 | Bold | Maximum adaptation, makes strong connections |

## 📁 Project Structure

```
dynamic-resume-creator/
├── app.py                    # Streamlit UI
├── core/
│   ├── __init__.py
│   ├── prompts.py            # System prompts for creativity levels
│   └── resume_generator.py   # Main generation logic
├── providers/
│   ├── __init__.py
│   ├── base.py               # Abstract provider interface
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── groq_provider.py
│   ├── ollama_provider.py
│   └── gemini_provider.py
├── requirements.txt
└── README.md
```

## 🔒 Privacy & Security

- API keys are stored in session memory only
- Keys are never written to disk or logged
- When using Ollama, your data never leaves your computer

## 🐛 Troubleshooting

### "Ollama not detected"
```bash
# Make sure Ollama is running
ollama serve

# Pull a model if you haven't
ollama pull llama3.3
```

### "API key invalid"
- Make sure there are no extra spaces when pasting
- Check that your API key has the correct permissions
- Verify your account has credits/access

### LaTeX doesn't compile
- The AI tries to match your sample's structure exactly
- If compilation fails, try a simpler sample resume
- Check for any special packages that might need to be included

## 📝 License

MIT License - feel free to use and modify!

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io) - UI framework
- [OpenAI](https://openai.com), [Anthropic](https://anthropic.com), [Groq](https://groq.com), [Google](https://ai.google.dev), [Ollama](https://ollama.ai) - LLM providers
