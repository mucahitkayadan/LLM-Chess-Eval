import chess
import chess.engine
from typing import Optional, Tuple

class ChessEngine:
    def __init__(self, engine_path: str = "stockfish"):
        """
        Initialize chess engine.
        
        Args:
            engine_path: Path to the chess engine executable
        """
        self.engine_path = engine_path
        self.engine = None
        
    def start(self):
        """Start the chess engine."""
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        
    def stop(self):
        """Stop the chess engine."""
        if self.engine:
            self.engine.quit()
            
    def get_move(self, board: chess.Board, skill_level: int = 20, time_limit: float = 0.1) -> Optional[chess.Move]:
        """
        Get move from engine at specified skill level.
        
        Args:
            board: Current board position
            skill_level: Engine skill level (0-20)
            time_limit: Time limit for move calculation in seconds
            
        Returns:
            Chess move or None if error
        """
        try:
            # Set skill level
            self.engine.configure({"Skill Level": skill_level})
            
            # Get move with time limit
            result = self.engine.play(
                board,
                chess.engine.Limit(time=time_limit)
            )
            
            return result.move
            
        except Exception as e:
            print(f"Error getting engine move: {str(e)}")
            return None 