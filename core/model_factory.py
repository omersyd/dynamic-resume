from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None
try:
    from langchain_community.chat_models import ChatOllama
except ImportError:
    ChatOllama = None


class ModelFactory:
    @staticmethod
    def get_model(
        provider: str,
        model_name: str,
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ) -> BaseChatModel:
        """
        Factory to return a LangChain ChatModel based on provider.
        """
        provider = provider.lower()

        if provider == "openai":
            return ChatOpenAI(
                model=model_name,
                api_key=api_key,
                temperature=temperature
            )

        elif provider == "anthropic":
            return ChatAnthropic(
                model=model_name,
                api_key=api_key,
                temperature=temperature
            )

        elif provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temperature,
                convert_system_message_to_human=True
            )

        elif provider == "groq":
            if ChatGroq is None:
                raise ImportError("langchain-groq is not installed.")
            return ChatGroq(
                model_name=model_name,
                groq_api_key=api_key,
                temperature=temperature
            )

        elif provider == "ollama":
            if ChatOllama is None:
                raise ImportError("langchain-community is not installed.")
            # Ollama is local, usually no key
            return ChatOllama(
                model=model_name,
                temperature=temperature,
                base_url="http://localhost:11434"
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")
