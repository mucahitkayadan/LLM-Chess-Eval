import asyncio
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from src.game_manager import GameManager
from src.llm_player import LLMPlayer
from src.results_manager import ResultsManager
import logging

async def main():
    # Load environment variables
    load_dotenv()
    
    # Get project root directory
    PROJECT_ROOT = Path(__file__).parent
    
    # Load configuration
    with open(PROJECT_ROOT / "config" / "config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
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
    for i, model1 in enumerate(config["models"]):
        for model2 in config["models"][i+1:]:
            white_player = LLMPlayer(model1["name"])
            black_player = LLMPlayer(model2["name"])
            
            for game_num in range(config["game"]["num_llm_vs_llm_games"]):
                print(f"Playing {model1['name']} vs {model2['name']}, game {game_num + 1}")
                
                result = await game_manager.play_llm_vs_llm(white_player, black_player)
                
                print(f"Result: {result['result']}")
                print(f"Moves: {' '.join(result['moves'])}")
                print(f"White illegal moves: {result['white_illegal_moves']}")
                print(f"Black illegal moves: {result['black_illegal_moves']}\n")

if __name__ == "__main__":
    asyncio.run(main()) 