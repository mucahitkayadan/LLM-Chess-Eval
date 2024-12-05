# LLM Chess Evaluation Framework 🧠♟️


## 🛠️ Technologies Used

<div align="center">

| Technology | Description |
|------------|-------------|
| ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) | Core programming language |
| ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white) | GPT-4 and variants |
| ![Anthropic](https://img.shields.io/badge/Anthropic-5A67D8?style=for-the-badge) | Claude models |
| ![LiteLLM](https://img.shields.io/badge/LiteLLM-FF6B6B?style=for-the-badge) | LLM provider integration |
| ![python-chess](https://img.shields.io/badge/python--chess-4D4D4D?style=for-the-badge) | Chess logic and board representation |
| ![Stockfish](https://img.shields.io/badge/Stockfish-FF9A00?style=for-the-badge) | Chess engine opponent |
| ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) | Data analysis |
| ![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black) | Visualization |
| ![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=for-the-badge) | Statistical visualization |

</div>

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

1. Edit the `.env` file and add your API keys:
- OPENAI_API_KEY: Get from [OpenAI](https://platform.openai.com/account/api-keys)
- ANTHROPIC_API_KEY: Get from [Anthropic](https://console.anthropic.com/account/keys)
- COHERE_API_KEY: Get from [Cohere](https://dashboard.cohere.ai/api-keys)
- PALM_API_KEY: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Clone the repository:

```bash
git clone https://github.com/mucahitkayadan/LLM-Chess-Eval.git
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Install Stockfish chess engine:
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

## Provider Configuration

The framework supports multiple LLM providers. Each provider requires its own API key:

1. **OpenAI**
   - Set `OPENAI_API_KEY` in `.env`
   - Models: GPT-4, GPT-4-turbo-preview

2. **Anthropic**
   - Set `ANTHROPIC_API_KEY` in `.env`
   - Models: Claude-3-sonnet, Claude-instant

3. **Cohere** (optional)
   - Set `COHERE_API_KEY` in `.env` if you want to use Cohere models
   - Models: command-nightly

The framework will automatically enable providers based on available API keys. You only need to set the keys for the providers you want to use.

### Adding New Providers

To add a new provider:

1. Add the provider configuration to `config/config.yaml`
2. Add the API key to your `.env` file
3. Update the key mapping in the code

Example provider configuration:
```yaml
new_provider:
  name: "new_provider"
  enabled: false  # Will be automatically enabled if an API key is present
  models:
    - name: "model-name"
      description: "Model description"
  rate_limit:
    requests_per_minute: 50
    retry_after: 20
```


## 📦 Dependencies

```txt
litellm>=1.10.1        # LLM provider integration
python-chess>=1.999    # Chess logic
pyyaml>=6.0.1         # Configuration management
python-dotenv>=1.0.0   # Environment variables
chess~=1.11.1         # Additional chess utilities
pandas~=2.2.3         # Data analysis
matplotlib~=3.9.3     # Plotting
seaborn~=0.13.2       # Statistical visualization
pytest>=7.0.0         # Testing
pytest-asyncio>=0.23.0 # Async testing
```