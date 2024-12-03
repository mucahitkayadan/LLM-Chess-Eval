import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ResultsManager:
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        
    def add_game_result(self, result: Dict):
        """Add a game result to the collection."""
        self.results.append(result)
        
    def save_results(self):
        """Save results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"chess_results_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
    def analyze_results(self):
        """Analyze results and generate visualizations."""
        if not self.results:
            logger.warning("No results to analyze")
            return
            
        df = pd.DataFrame(self.results)
        
        # Create output directory for plots
        plots_dir = self.output_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # Separate engine games and LLM vs LLM games
        engine_games = df[df['engine_skill_level'].notna()]
        llm_games = df[df['engine_skill_level'].isna()]
        
        if not engine_games.empty:
            self._analyze_engine_games(engine_games, plots_dir)
            
        if not llm_games.empty:
            self._analyze_llm_games(llm_games, plots_dir)
        
        # Generate summary statistics
        self._generate_summary_report(df)
        
    def _analyze_engine_games(self, df: pd.DataFrame, plots_dir: Path):
        """Analyze games against the chess engine."""
        # Win rates by model
        plt.figure(figsize=(12, 6))
        win_rates = df.groupby('llm_model').agg({
            'result': lambda x: (x == 'llm_won').mean()
        })
        
        sns.barplot(data=win_rates.reset_index(), x='llm_model', y='result')
        plt.title('Win Rates vs Engine by Model')
        plt.xlabel('Model')
        plt.ylabel('Win Rate')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(plots_dir / 'engine_win_rates.png')
        plt.close()
        
        # Performance vs engine levels
        self._plot_engine_performance(df, plots_dir)
        
    def _analyze_llm_games(self, df: pd.DataFrame, plots_dir: Path):
        """Analyze LLM vs LLM games."""
        plt.figure(figsize=(12, 6))
        
        # Calculate win rates for white and black
        model_stats = pd.DataFrame()
        for model in df['white_model'].unique():
            white_games = df[df['white_model'] == model]
            black_games = df[df['black_model'] == model]
            
            white_wins = (white_games['result'] == 'white_won').mean()
            black_wins = (black_games['result'] == 'black_won').mean()
            
            model_stats.loc[model, 'White Win Rate'] = white_wins
            model_stats.loc[model, 'Black Win Rate'] = black_wins
        
        model_stats.plot(kind='bar')
        plt.title('Model Performance by Color')
        plt.xlabel('Model')
        plt.ylabel('Win Rate')
        plt.legend()
        plt.tight_layout()
        plt.savefig(plots_dir / 'llm_vs_llm_performance.png')
        plt.close()
        
    def _plot_engine_performance(self, df: pd.DataFrame, plots_dir: Path):
        """Plot performance against different engine levels."""
        plt.figure(figsize=(12, 6))
        
        performance = df.pivot_table(
            index='engine_skill_level',
            columns='llm_model',
            values='result',
            aggfunc=lambda x: (x == 'llm_won').mean()
        )
        
        performance.plot(marker='o')
        plt.title('Win Rate vs Engine Skill Level')
        plt.xlabel('Engine Skill Level')
        plt.ylabel('Win Rate')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(plots_dir / 'engine_performance.png')
        plt.close()
        
    def _generate_summary_report(self, df: pd.DataFrame):
        """Generate a text report with summary statistics."""
        report = ["Chess LLM Evaluation Summary", "=" * 30, ""]
        
        # Overall statistics
        report.append("Overall Statistics:")
        report.append(f"Total games played: {len(df)}")
        report.append(f"Games won by LLMs: {(df['result'] == 'llm_won').sum()}")
        report.append(f"Games won by engine: {(df['result'] == 'engine_won').sum()}")
        report.append("")
        
        # Per model statistics
        report.append("Per Model Statistics:")
        for model in df['llm_model'].unique():
            model_df = df[df['llm_model'] == model]
            report.append(f"\n{model}:")
            report.append(f"Games played: {len(model_df)}")
            report.append(f"Win rate: {(model_df['result'] == 'llm_won').mean():.2%}")
            report.append(f"Average illegal moves: {model_df['illegal_moves'].mean():.2f}")
        
        # Save report
        with open(self.output_dir / "summary_report.txt", 'w') as f:
            f.write('\n'.join(report))