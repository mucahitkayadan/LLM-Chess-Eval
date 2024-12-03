import chess

class MoveValidator:
    def __init__(self):
        self.illegal_moves_count = {}  # Maps model_name to count of illegal moves
        
    def reset_counter(self, model_name: str):
        """Reset illegal moves counter for a model."""
        self.illegal_moves_count[model_name] = 0
        
    def validate_move(self, board: chess.Board, move_str: str, model_name: str) -> tuple[bool, chess.Move | None]:
        """
        Validate a move string and return whether it's legal and the parsed move.
        
        Args:
            board: Current chess board state
            move_str: Move in algebraic notation
            model_name: Name of the model making the move
            
        Returns:
            Tuple of (is_legal, parsed_move)
        """
        try:
            # Clean the move string
            move_str = move_str.strip()
            
            # Parse the move
            move = board.parse_san(move_str)
            
            # Check if move is legal
            if move in board.legal_moves:
                return True, move
                
            self.illegal_moves_count[model_name] = self.illegal_moves_count.get(model_name, 0) + 1
            return False, None
            
        except ValueError:
            # Invalid move format
            self.illegal_moves_count[model_name] = self.illegal_moves_count.get(model_name, 0) + 1
            return False, None
            
    def get_illegal_moves_count(self, model_name: str) -> int:
        """Get number of illegal moves made by a model."""
        return self.illegal_moves_count.get(model_name, 0) 