import chess
from typing import Optional, List, Dict
from datetime import datetime
from src.chess_engine import ChessEngine
from src.llm_player import LLMPlayer
from src.move_validator import MoveValidator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self):
        self.board = chess.Board()
        self.move_validator = MoveValidator()
        self.game_history: List[Dict] = []
        
    def reset_game(self):
        """Reset the game state."""
        self.board = chess.Board()
        
    async def play_llm_vs_engine(
        self,
        llm_player: LLMPlayer,
        engine_path: str,
        skill_level: int,
        llm_plays_white: bool = True
    ) -> Dict:
        """
        Play a game between an LLM and the chess engine.
        
        Args:
            llm_player: The LLM player
            engine_path: Path to chess engine
            skill_level: Engine skill level
            llm_plays_white: Whether LLM plays white
            
        Returns:
            Game result dictionary
        """
        logger.info(f"Starting game: {llm_player.model_name} vs Engine (skill level {skill_level})")
        logger.info(f"LLM playing {'white' if llm_plays_white else 'black'}")
        
        self.reset_game()
        self.move_validator.reset_counter(llm_player.model_name)
        
        engine = ChessEngine(engine_path)
        engine.start()
        
        game_record = {
            "timestamp": datetime.now().isoformat(),
            "llm_model": llm_player.model_name,
            "engine_skill_level": skill_level,
            "llm_plays_white": llm_plays_white,
            "moves": [],
            "result": None,
            "illegal_moves": 0
        }
        
        try:
            while not self.board.is_game_over():
                logger.debug(f"Current position:\n{self.board}")
                
                is_llm_turn = (self.board.turn == chess.WHITE) == llm_plays_white
                
                if is_llm_turn:
                    logger.info("LLM's turn")
                    move_str = llm_player.get_move(
                        str(self.board),
                        self._format_move_history(),
                        "White" if self.board.turn == chess.WHITE else "Black"
                    )
                    
                    is_legal, move = self.move_validator.validate_move(
                        self.board,
                        move_str,
                        llm_player.model_name
                    )
                    
                    if not is_legal:
                        illegal_count = self.move_validator.get_illegal_moves_count(llm_player.model_name)
                        logger.warning(f"Illegal move by {llm_player.model_name}: {move_str} (Count: {illegal_count})")
                        if illegal_count >= 3:
                            logger.info(f"Game over - {llm_player.model_name} made too many illegal moves")
                            game_record["result"] = "engine_won_illegal_moves"
                            break
                        continue
                        
                else:
                    # Engine's turn
                    move = engine.get_move(self.board, skill_level)
                    if not move:
                        game_record["result"] = "error_engine_move"
                        break
                        
                # Make the move
                self.board.push(move)
                game_record["moves"].append(str(move))
                
            # Record final game state if not already set
            if not game_record["result"]:
                if self.board.is_checkmate():
                    game_record["result"] = "llm_won" if is_llm_turn else "engine_won"
                elif self.board.is_stalemate():
                    game_record["result"] = "draw_stalemate"
                elif self.board.is_insufficient_material():
                    game_record["result"] = "draw_insufficient_material"
                elif self.board.is_fifty_moves():
                    game_record["result"] = "draw_fifty_moves"
                elif self.board.is_repetition():
                    game_record["result"] = "draw_repetition"
                    
        finally:
            engine.stop()
            
        game_record["illegal_moves"] = self.move_validator.get_illegal_moves_count(llm_player.model_name)
        self.game_history.append(game_record)
        return game_record
        
    async def play_llm_vs_llm(
        self,
        white_player: LLMPlayer,
        black_player: LLMPlayer
    ) -> Dict:
        """
        Play a game between two LLMs.
        
        Args:
            white_player: LLM playing white
            black_player: LLM playing black
            
        Returns:
            Game result dictionary
        """
        self.reset_game()
        self.move_validator.reset_counter(white_player.model_name)
        self.move_validator.reset_counter(black_player.model_name)
        
        game_record = {
            "timestamp": datetime.now().isoformat(),
            "white_model": white_player.model_name,
            "black_model": black_player.model_name,
            "moves": [],
            "result": None,
            "white_illegal_moves": 0,
            "black_illegal_moves": 0
        }
        
        while not self.board.is_game_over():
            current_player = white_player if self.board.turn == chess.WHITE else black_player
            
            move_str = current_player.get_move(
                str(self.board),
                self._format_move_history(),
                "White" if self.board.turn == chess.WHITE else "Black"
            )
            
            is_legal, move = self.move_validator.validate_move(
                self.board,
                move_str,
                current_player.model_name
            )
            
            if not is_legal:
                if self.move_validator.get_illegal_moves_count(current_player.model_name) >= 3:
                    game_record["result"] = "black_won_illegal_moves" if self.board.turn == chess.WHITE else "white_won_illegal_moves"
                    break
                continue
                
            # Make the move
            self.board.push(move)
            game_record["moves"].append(str(move))
            
        # Record final game state if not already set
        if not game_record["result"]:
            if self.board.is_checkmate():
                game_record["result"] = "black_won" if self.board.turn == chess.WHITE else "white_won"
            elif self.board.is_stalemate():
                game_record["result"] = "draw_stalemate"
            elif self.board.is_insufficient_material():
                game_record["result"] = "draw_insufficient_material"
            elif self.board.is_fifty_moves():
                game_record["result"] = "draw_fifty_moves"
            elif self.board.is_repetition():
                game_record["result"] = "draw_repetition"
                
        game_record["white_illegal_moves"] = self.move_validator.get_illegal_moves_count(white_player.model_name)
        game_record["black_illegal_moves"] = self.move_validator.get_illegal_moves_count(black_player.model_name)
        self.game_history.append(game_record)
        return game_record
        
    def _format_move_history(self) -> str:
        """Format the move history for LLM consumption."""
        moves = []
        temp_board = chess.Board()
        
        for i, move in enumerate(self.board.move_stack):
            try:
                san_move = temp_board.san(move)
                if i % 2 == 0:
                    moves.append(f"{i//2 + 1}. {san_move}")
                else:
                    moves.append(san_move)
                temp_board.push(move)
            except Exception as e:
                print(f"Error formatting move {move}: {str(e)}")
                continue
                
        return " ".join(moves) 