import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict

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
        df = pd.DataFrame(self.results)
        
        # Create output directory for plots
        plots_dir = self.output_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # 1. Win rates by model
        self._plot_win_rates(df, plots_dir)
        
        # 2. Illegal moves analysis
        self._plot_illegal_moves(df, plots_dir)
        
        # 3. Performance vs engine levels
        self._plot_engine_performance(df, plots_dir)
        
        # Generate summary statistics
        self._generate_summary_report(df)
        
    def _plot_win_rates(self, df: pd.DataFrame, plots_dir: Path):
        """Plot win rates for each model."""
        plt.figure(figsize=(12, 6))
        
        # Calculate win rates
        win_rates = df[df['result'].isin(['llm_won', 'engine_won'])].groupby('llm_model').agg({
            'result': lambda x: (x == 'llm_won').mean()
        })
        
        sns.barplot(data=win_rates.reset_index(), x='llm_model', y='result')
        plt.title('Win Rates by Model')
        plt.xlabel('Model')
        plt.ylabel('Win Rate')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(plots_dir / 'win_rates.png')
        plt.close()
        
    def _plot_illegal_moves(self, df: pd.DataFrame, plots_dir: Path):
        """Plot illegal moves statistics."""
        plt.figure(figsize=(12, 6))
        
        sns.boxplot(data=df, x='llm_model', y='illegal_moves')
        plt.title('Illegal Moves Distribution by Model')
        plt.xlabel('Model')
        plt.ylabel('Number of Illegal Moves')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(plots_dir / 'illegal_moves.png')
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