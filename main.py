import asyncio
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from src.game_manager import GameManager
from src.llm_player import LLMPlayer
from src.results_manager import ResultsManager
import logging
import litellm

# Configure logging with more verbose format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_env_var(var_name: str, env_file_only: bool = True) -> str:
    """
    Get environment variable with option to ignore system environment.
    
    Args:
        var_name: Name of the environment variable
        env_file_only: If True, only look in .env file, ignore system environment
    """
    if env_file_only:
        # Load only from .env file
        from dotenv import dotenv_values
        env_vars = dotenv_values()
        value = env_vars.get(var_name)
        logger.info(f"Loading {var_name} from .env file: {'Found' if value else 'Not found'}")
        return value
    else:
        # Load from all sources
        value = os.getenv(var_name)
        logger.info(f"Loading {var_name} from environment: {'Found' if value else 'Not found'}")
        return value

def verify_api_keys(config: dict):
    """
    Verify API keys and automatically enable/disable providers based on available keys.
    Returns modified config.
    """
    key_mapping = {
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'cohere': 'COHERE_API_KEY'
    }
    
    for provider, provider_config in config["providers"].items():
        env_var = key_mapping.get(provider)
        # Only load from .env file, ignore system environment
        api_key = get_env_var(env_var, env_file_only=True)
        
        if api_key:
            logger.info(f"{provider.upper()} API Key found in .env: {api_key[:10]}...")
            provider_config["enabled"] = True
            # Set the key in litellm explicitly
            if provider == 'openai':
                litellm.openai_key = api_key
                os.environ["OPENAI_API_KEY"] = api_key  # Override any system variable
            elif provider == 'anthropic':
                litellm.anthropic_key = api_key
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif provider == 'cohere':
                litellm.cohere_key = api_key
                os.environ["COHERE_API_KEY"] = api_key
        else:
            logger.warning(f"No API key found in .env for {provider} - provider will be disabled")
            provider_config["enabled"] = False
            # Clear any system environment variables
            if provider == 'openai':
                os.environ.pop("OPENAI_API_KEY", None)
            elif provider == 'anthropic':
                os.environ.pop("ANTHROPIC_API_KEY", None)
            elif provider == 'cohere':
                os.environ.pop("COHERE_API_KEY", None)
    
    # Log enabled providers
    enabled_providers = [p for p, c in config["providers"].items() if c["enabled"]]
    logger.info(f"Enabled providers: {', '.join(enabled_providers)}")
    
    return config

def debug_environment():
    """Debug environment variables from all sources."""
    from dotenv import dotenv_values
    
    # Check .env file
    env_file_vars = dotenv_values()
    logger.info("Variables in .env file:")
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "COHERE_API_KEY"]:
        value = env_file_vars.get(key)
        logger.info(f"{key}: {'Found' if value else 'Not found'} {value[:10] + '...' if value else ''}")
    
    # Check system environment
    logger.info("\nVariables in system environment:")
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "COHERE_API_KEY"]:
        value = os.environ.get(key)
        logger.info(f"{key}: {'Found' if value else 'Not found'} {value[:10] + '...' if value else ''}")
    
    # Check litellm configuration
    logger.info("\nVariables in litellm:")
    logger.info(f"openai_key: {'Found' if litellm.openai_key else 'Not found'} {litellm.openai_key[:10] + '...' if litellm.openai_key else ''}")
    logger.info(f"anthropic_key: {'Found' if litellm.anthropic_key else 'Not found'} {litellm.anthropic_key[:10] + '...' if litellm.anthropic_key else ''}")
    logger.info(f"cohere_key: {'Found' if litellm.cohere_key else 'Not found'} {litellm.cohere_key[:10] + '...' if litellm.cohere_key else ''}")

async def main():
    # Clear any existing environment variables first
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "COHERE_API_KEY"]:
        os.environ.pop(key, None)
    
    # Load environment variables from .env file only
    load_dotenv(override=True)
    
    # Get project root directory
    PROJECT_ROOT = Path(__file__).parent
    
    # Load configuration
    with open(PROJECT_ROOT / "config" / "config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Verify API keys and update config
    config = verify_api_keys(config)
    
    # Continue only if at least one provider is enabled
    enabled_providers = [p for p, c in config["providers"].items() if c["enabled"]]
    if not enabled_providers:
        logger.error("No providers enabled - please set at least one API key")
        return
    
    # Set stockfish path - prefer env variable, fallback to relative path
    stockfish_path = os.getenv("STOCKFISH_PATH")
    if stockfish_path:
        # Convert relative path from .env to absolute path from project root
        engine_path = (PROJECT_ROOT / stockfish_path).resolve()
    else:
        engine_path = (PROJECT_ROOT / "stockfish" / "stockfish.exe").resolve()
    
    print(f"Looking for Stockfish at: {engine_path}")
    
    if not engine_path.exists():
        raise FileNotFoundError(f"Stockfish not found at {engine_path}. Current directory: {os.getcwd()}")
        
    config["engine"]["path"] = str(engine_path)
    
    game_manager = GameManager()
    
    # Initialize results manager
    results_manager = ResultsManager()
    
    # LLM vs Engine matches
    for provider_config in config["providers"].values():
        if not provider_config["enabled"]:
            continue
            
        for model in provider_config["models"]:
            try:
                llm_player = LLMPlayer(model["name"], provider_config)
                
                for skill_level in config["engine"]["skill_levels"]:
                    for game_num in range(config["game"]["num_games_per_skill_level"]):
                        result = await game_manager.play_llm_vs_engine(
                            llm_player,
                            config["engine"]["path"],
                            skill_level
                        )
                        results_manager.add_game_result(result)
                        
            except ValueError as e:
                logger.warning(f"Skipping model {model['name']}: {str(e)}")
                continue
    
    # Analyze and save results
    results_manager.analyze_results()
    results_manager.save_results()
    
    # LLM vs LLM matches
    for provider1, config1 in config["providers"].items():
        if not config1["enabled"]:
            continue
            
        for provider2, config2 in config["providers"].items():
            if not config2["enabled"] or provider2 <= provider1:  # Avoid duplicate matches and self-matches
                continue
                
            for model1 in config1["models"]:
                for model2 in config2["models"]:
                    try:
                        white_player = LLMPlayer(model1["name"], config1)
                        black_player = LLMPlayer(model2["name"], config2)
                        
                        for game_num in range(config["game"]["num_llm_vs_llm_games"]):
                            logger.info(f"Playing {model1['name']} vs {model2['name']}, game {game_num + 1}")
                            
                            result = await game_manager.play_llm_vs_llm(white_player, black_player)
                            results_manager.add_game_result(result)
                            
                            logger.info(f"Result: {result['result']}")
                            logger.info(f"Moves: {' '.join(result['moves'])}")
                            logger.info(f"White illegal moves: {result['white_illegal_moves']}")
                            logger.info(f"Black illegal moves: {result['black_illegal_moves']}\n")
                            
                    except ValueError as e:
                        logger.warning(f"Skipping match {model1['name']} vs {model2['name']}: {str(e)}")
                        continue

if __name__ == "__main__":
    asyncio.run(main()) 