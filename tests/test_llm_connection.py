import os
import pytest
from dotenv import load_dotenv
import yaml
from pathlib import Path
import litellm
from src.llm_player import LLMPlayer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables and config
load_dotenv()
PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "config" / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

@pytest.fixture(autouse=True)
def setup_litellm():
    """Setup litellm configuration before each test."""
    # Clear any existing configuration
    litellm.openai_key = None
    litellm.anthropic_key = None
    litellm.cohere_key = None
    
    # Load keys from environment
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if openai_key:
        litellm.openai_key = openai_key
        logger.info(f"Set OpenAI key: {openai_key[:10]}...")
    if anthropic_key:
        litellm.anthropic_key = anthropic_key
        logger.info(f"Set Anthropic key: {anthropic_key[:10]}...")
    
    yield

def test_api_keys_present():
    """Test if API keys are properly set in environment."""
    key_mapping = {
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'cohere': 'COHERE_API_KEY'
    }
    
    for provider, provider_config in config["providers"].items():
        if provider_config["enabled"]:
            env_var = key_mapping.get(provider)
            api_key = os.getenv(env_var)
            logger.info(f"Testing {provider} API key...")
            logger.info(f"API key found: {'Yes' if api_key else 'No'}")
            logger.info(f"API key length: {len(api_key) if api_key else 0}")
            logger.info(f"API key starts with: {api_key[:10] + '...' if api_key else 'None'}")
            assert api_key is not None, f"API key not found for enabled provider {provider}"
            assert len(api_key) > 0, f"API key is empty for provider {provider}"

@pytest.mark.asyncio
async def test_openai_connection():
    """Test OpenAI API connection."""
    if not config["providers"]["openai"]["enabled"]:
        pytest.skip("OpenAI provider is not enabled")
    
    api_key = os.getenv("OPENAI_API_KEY")
    logger.info(f"Using OpenAI API key starting with: {api_key[:10]}...")
    
    # Reset litellm configuration
    litellm.openai_key = None
    litellm.anthropic_key = None
    
    try:
        # Set the API key explicitly
        litellm.openai_key = api_key
        
        response = litellm.completion(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[{"role": "user", "content": "Say 'test' if you can read this."}],
            max_tokens=5,
            api_key=api_key  # Pass API key explicitly
        )
        assert response.choices[0].message.content.lower().strip() == "test"
    except Exception as e:
        pytest.fail(f"OpenAI connection failed: {str(e)}")

@pytest.mark.asyncio
async def test_anthropic_connection():
    """Test Anthropic API connection."""
    if not config["providers"]["anthropic"]["enabled"]:
        pytest.skip("Anthropic provider is not enabled")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    logger.info(f"Using Anthropic API key starting with: {api_key[:10]}...")
    
    # Reset litellm configuration
    litellm.openai_key = None
    litellm.anthropic_key = None
    
    try:
        # Set the API key explicitly
        litellm.anthropic_key = api_key
        
        response = litellm.completion(
            model="claude-instant-1.2",  # Use cheaper model for testing
            messages=[{"role": "user", "content": "Say 'test' if you can read this."}],
            max_tokens=5,
            api_key=api_key  # Pass API key explicitly
        )
        assert response.choices[0].message.content.lower().strip() == "test"
    except Exception as e:
        pytest.fail(f"Anthropic connection failed: {str(e)}")

def test_model_initialization():
    """Test if models can be properly initialized."""
    for provider, provider_config in config["providers"].items():
        if not provider_config["enabled"]:
            continue
        
        logger.info(f"Testing initialization for provider: {provider}")
        for model in provider_config["models"]:
            try:
                player = LLMPlayer(model["name"], provider_config)
                assert player.api_key is not None
                assert player.provider_name == provider_config["name"]
                logger.info(f"Successfully initialized {model['name']} with API key starting with: {player.api_key[:10]}...")
            except Exception as e:
                pytest.fail(f"Failed to initialize {model['name']}: {str(e)}")

def test_chess_prompt_format():
    """Test if chess prompts are properly formatted."""
    test_board = """
rnbqkbnr
pppppppp
........
........
........
........
PPPPPPPP
RNBQKBNR
"""
    test_history = "1. e4"
    
    for provider, provider_config in config["providers"].items():
        if not provider_config["enabled"]:
            continue
            
        for model in provider_config["models"]:
            try:
                player = LLMPlayer(model["name"], provider_config)
                prompt = player.get_move(test_board, test_history, "Black")
                assert isinstance(prompt, str), "Prompt should be a string"
            except Exception as e:
                pytest.fail(f"Failed to format prompt for {model['name']}: {str(e)}") 