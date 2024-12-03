import pytest
from pathlib import Path
import chess
from src.chess_engine import ChessEngine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_stockfish_path():
    """Test if Stockfish path is valid."""
    PROJECT_ROOT = Path(__file__).parent.parent
    stockfish_path = os.getenv("STOCKFISH_PATH")
    if stockfish_path:
        engine_path = (PROJECT_ROOT / stockfish_path).resolve()
    else:
        engine_path = (PROJECT_ROOT / "stockfish" / "stockfish.exe").resolve()
        
    assert engine_path.exists(), f"Stockfish not found at {engine_path}"

def test_engine_initialization():
    """Test if chess engine can be initialized."""
    engine = ChessEngine(os.getenv("STOCKFISH_PATH"))
    try:
        engine.start()
        assert engine.engine is not None
    finally:
        engine.stop()

def test_engine_move_generation():
    """Test if engine can generate moves."""
    engine = ChessEngine(os.getenv("STOCKFISH_PATH"))
    board = chess.Board()
    
    try:
        engine.start()
        move = engine.get_move(board, skill_level=10)
        assert move is not None
        assert move in board.legal_moves
    finally:
        engine.stop()

def test_skill_levels():
    """Test different skill levels."""
    engine = ChessEngine(os.getenv("STOCKFISH_PATH"))
    board = chess.Board()
    
    try:
        engine.start()
        for skill_level in [0, 5, 10, 15, 20]:
            move = engine.get_move(board, skill_level=skill_level)
            assert move is not None
            assert move in board.legal_moves
    finally:
        engine.stop() 