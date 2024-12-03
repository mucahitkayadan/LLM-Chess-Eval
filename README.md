# LLM Chess Evaluation Framework 🧠♟️

A sophisticated framework for evaluating Large Language Models' chess-playing capabilities through matches against Stockfish and other LLMs.

## 🌟 Features

- **Multi-Model Support**: Test various LLMs including:
  - OpenAI GPT-4 and variants
  - Anthropic Claude 3
  - Cohere Command
  
- **Comprehensive Evaluation**:
  - LLM vs Stockfish matches at different skill levels
  - LLM vs LLM matches
  - Illegal move tracking and analysis
  
- **Advanced Analytics**:
  - Win rate analysis
  - Performance visualization
  - Detailed statistical reporting
  - Game move history tracking

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Stockfish chess engine
- API keys for the LLMs you want to test

2. Edit the `.env` file and add your API keys:
- OPENAI_API_KEY: Get from [OpenAI](https://platform.openai.com/account/api-keys)
- ANTHROPIC_API_KEY: Get from [Anthropic](https://console.anthropic.com/account/keys)
- COHERE_API_KEY: Get from [Cohere](https://dashboard.cohere.ai/api-keys)
- PALM_API_KEY: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

1. Clone the repository:

```bash
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Install Stockfish chess engine:
   - Windows: Download from [Stockfish website](https://stockfishchess.org/download/)
   - Linux: `sudo apt-get install stockfish`
   - macOS: `brew install stockfish`

### Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Configure your API keys in `.env`:

```env
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
COHERE_API_KEY=your-key-here
```

3. Set up Stockfish path in `.env`:

```env
STOCKFISH_PATH=stockfish/stockfish.exe  
```

4. Customize `config/config.yaml` for:
   - Model selection
   - Game parameters
   - Engine skill levels
   - Rate limiting settings

## 🎮 Usage

Run the evaluation:

```bash
python main.py
```

### Available Game Modes

1. **LLM vs Stockfish**
   - Tests LLMs against various Stockfish skill levels
   - Tracks win rates and move quality
   - Analyzes performance patterns

2. **LLM vs LLM**
   - Pits different LLMs against each other
   - Compares relative strengths
   - Evaluates strategic differences

## 📊 Results Analysis

The framework generates comprehensive analysis in the `results` directory:

```
results/
├── plots/
│   ├── win_rates.png
│   ├── illegal_moves.png
│   └── engine_performance.png
├── chess_results_[timestamp].json
└── summary_report.txt
```

### Visualization Types

- **Win Rate Analysis**: Bar charts showing success rates against Stockfish
- **Illegal Move Distribution**: Box plots of illegal move frequencies
- **Engine Performance**: Line graphs of performance across skill levels

## 🛠️ Project Structure

```
.
├── config/
│   └── config.yaml         # Configuration settings
├── src/
│   ├── chess_engine.py     # Stockfish interface
│   ├── game_manager.py     # Game orchestration
│   ├── llm_player.py       # LLM interaction
│   ├── move_validator.py   # Move validation
│   ├── prompts.py         # LLM prompts
│   └── results_manager.py  # Analysis & visualization
├── .env                    # Environment variables
├── main.py                # Entry point
└── requirements.txt       # Dependencies
```

## 📈 Performance Metrics

The framework tracks several key metrics:
- Win/loss/draw ratios
- Illegal move frequency
- Game length statistics
- Move quality assessment
- Time per move

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Chess engine: [Stockfish](https://stockfishchess.org/)
- LLM providers: OpenAI, Anthropic, and Cohere
- Python chess library contributors

## 📧 Contact

For questions and feedback:
- Create an issue in the repository
- Contact: mujakayadan@outlook.com

---
Made with ❤️ by Muja Kayadan
```
