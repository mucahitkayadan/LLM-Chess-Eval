import os
import logging
import time
from typing import Optional, Dict

import litellm
from litellm import completion
from src.prompts import CHESS_SYSTEM_PROMPT, CHESS_USER_PROMPT_TEMPLATE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMPlayer:
    def __init__(self, model_name: str, provider_config: Dict):
        """
        Initialize an LLM player with rate limiting.
        
        Args:
            model_name: The model identifier
            provider_config: Configuration for the provider including rate limits
        """
        self.model_name = model_name
        self.provider_config = provider_config
        self.provider_name = provider_config.get('name')
        self.last_request_time = 0
        self.requests_this_minute = 0
        
        # Verify API keys and provider status
        if not provider_config.get('enabled', False):
            raise ValueError(f"Provider {self.provider_name} is not enabled in config")
            
        self.api_key = self._get_api_key()
        if not self.api_key:
            raise ValueError(f"API key not found for provider {self.provider_name}")
            
        # Set API key in litellm based on provider
        if self.provider_name == 'openai':
            litellm.openai_key = self.api_key
        elif self.provider_name == 'anthropic':
            litellm.anthropic_key = self.api_key
        elif self.provider_name == 'cohere':
            litellm.cohere_key = self.api_key
            
        logger.info(f"Initialized {self.provider_name} model: {model_name}")
        
    def _get_api_key(self) -> Optional[str]:
        """Get API key for provider."""
        key_mapping = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'cohere': 'COHERE_API_KEY'
        }
        
        env_var = key_mapping.get(self.provider_name)
        if not env_var:
            return None
            
        # Load only from .env file
        from dotenv import dotenv_values
        env_vars = dotenv_values()
        api_key = env_vars.get(env_var)
        
        logger.info(f"Using API key for {self.provider_name} from .env: {api_key[:10] if api_key else 'None'}")
        return api_key
        
    def _handle_rate_limit(self):
        """Handle rate limiting."""
        current_time = time.time()
        if current_time - self.last_request_time >= 60:
            # Reset counter after a minute
            self.requests_this_minute = 0
            self.last_request_time = current_time
            
        if self.requests_this_minute >= self.provider_config['rate_limit']['requests_per_minute']:
            sleep_time = self.provider_config['rate_limit']['retry_after']
            logger.warning(f"Rate limit reached, waiting {sleep_time} seconds")
            time.sleep(sleep_time)
            self.requests_this_minute = 0
            
        self.requests_this_minute += 1
        
    def get_move(self, board_ascii: str, move_history: str, side_to_move: str) -> str:
        """
        Get the next move from the LLM.
        """
        self._handle_rate_limit()
        
        # Ensure API key is set for this request
        if self.provider_name == 'openai':
            litellm.openai_key = self.api_key
        elif self.provider_name == 'anthropic':
            litellm.anthropic_key = self.api_key
        elif self.provider_name == 'cohere':
            litellm.cohere_key = self.api_key
            
        litellm.set_verbose = True
        try:
            logger.info(f"Requesting move from {self.model_name} using {self.provider_name} key: {self.api_key[:10]}...")
            logger.debug(f"Current board:\n{board_ascii}")
            logger.debug(f"Move history: {move_history}")
            
            prompt = CHESS_USER_PROMPT_TEMPLATE.format(
                board_ascii=board_ascii,
                move_history=move_history,
                side_to_move=side_to_move
            )
            
            logger.debug(f"Sending prompt to LLM:\n{prompt}")
            
            # Add api_key explicitly in the completion call
            response = completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": CHESS_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10,
                api_key=self.api_key
            )
            
            move = response.choices[0].message.content.strip()
            logger.info(f"LLM {self.model_name} suggested move: {move}")
            
            return move
            
        except Exception as e:
            logger.error(f"Error getting move from {self.model_name}: {str(e)}")
            # Return an obviously invalid move to trigger the illegal move counter
            return "ERROR" 