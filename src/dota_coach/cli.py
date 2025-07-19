# DotA Coach CLI Module
# Command-line interface for manual testing and coaching simulation
# Phase 1: No real-time GSI, manual input for testing ML predictions

import click
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from .config import Config
from .constants import ConstantsTracker
from .data_flattener import DataFlattener
from .hero_mapping import HeroMapper


class DotACoachCLI:
    """Command-line interface for DotA Coach system."""
    
    def __init__(self):
        """Initialize CLI with configuration and modules."""
        self.config = Config()
        self.constants_tracker = ConstantsTracker(self.config)
        self.data_flattener = DataFlattener(self.config)
        self.hero_mapper = HeroMapper()
        
        # Set up logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging for the CLI."""
        log_level = self.config.get('logging.level', 'INFO')
        log_format = self.config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format
        )
        
        self.logger = logging.getLogger(__name__)
    
    def simulate_coach_recommendation(self, hero: str, lane: str, opponents: List[str] = None) -> Dict[str, Any]:
        """
        Simulate coaching recommendations for given inputs.
        
        Args:
            hero (str): Hero name from pool.
            lane (str): Lane assignment.
            opponents (List[str], optional): Opponent heroes.
            
        Returns:
            Dict[str, Any]: Coaching recommendations.
        """
        # This is a placeholder implementation for Phase 1
        # In future phases, this would use trained ML models
        
        recommendations = {
            'hero': hero,
            'lane': lane,
            'opponents': opponents or [],
            'starting_items': self._get_starting_items_recommendation(hero, opponents),
            'first_skill': self._get_first_skill_recommendation(hero, opponents),
            'early_game_strategy': self._get_early_game_strategy(hero, lane, opponents),
            'item_build': self._get_item_build_recommendation(hero, opponents),
            'confidence': 0.75  # Placeholder confidence score
        }
        
        return recommendations
    
    def _get_starting_items_recommendation(self, hero: str, opponents: List[str] = None) -> List[str]:
        """Get starting items recommendation for hero."""
        # Placeholder logic - would be replaced with ML model
        base_support_items = ['tango', 'clarity', 'observer_ward', 'sentry_ward']
        
        if hero == 'vengeful_spirit':
            return base_support_items + ['branches', 'faerie_fire']
        elif hero == 'witch_doctor':
            return base_support_items + ['branches', 'mango']
        elif hero == 'lich':
            return base_support_items + ['branches', 'mango']
        elif hero == 'lion':
            return base_support_items + ['branches', 'mango']
        elif hero == 'undying':
            return base_support_items + ['branches', 'gauntlets']
        elif hero == 'shadow_shaman':
            return base_support_items + ['branches', 'mango']
        else:
            return base_support_items
    
    def _get_first_skill_recommendation(self, hero: str, opponents: List[str] = None) -> str:
        """Get first skill recommendation for hero."""
        # Placeholder logic - would be replaced with ML model
        first_skills = {
            'vengeful_spirit': 'magic_missile',
            'witch_doctor': 'paralyzing_cask',
            'lich': 'frost_blast',
            'lion': 'earth_spike',
            'undying': 'decay',
            'shadow_shaman': 'ether_shock'
        }
        
        return first_skills.get(hero, 'unknown')
    
    def _get_early_game_strategy(self, hero: str, lane: str, opponents: List[str] = None) -> str:
        """Get early game strategy recommendation."""
        # Placeholder logic - would be replaced with ML model
        if lane == 'safe':
            return f"Focus on protecting your carry and harassing enemies. Ward river and jungle entrances."
        elif lane == 'off':
            return f"Play defensively, secure ranged creeps, and look for opportunities to disrupt enemy farm."
        else:
            return f"Roam between lanes, secure runes, and create space for your cores."
    
    def _get_item_build_recommendation(self, hero: str, opponents: List[str] = None) -> List[str]:
        """Get item build progression recommendation."""
        # Placeholder logic - would be replaced with ML model
        base_progression = ['boots', 'magic_wand', 'arcane_boots', 'force_staff']
        
        if hero in ['lion', 'shadow_shaman']:
            return base_progression + ['blink_dagger', 'aghanims_scepter']
        elif hero == 'witch_doctor':
            return base_progression + ['glimmer_cape', 'aghanims_scepter']
        else:
            return base_progression + ['glimmer_cape', 'lotus_orb']
    
    def display_recommendations(self, recommendations: Dict[str, Any]) -> None:
        """Display coaching recommendations in a formatted way."""
        click.echo("\n" + "="*60)
        click.echo(f"🎯 DOTA COACH RECOMMENDATIONS")
        click.echo("="*60)
        
        click.echo(f"\n📋 MATCH SETUP:")
        click.echo(f"   Hero: {recommendations['hero'].replace('_', ' ').title()}")
        click.echo(f"   Lane: {recommendations['lane'].title()}")
        if recommendations['opponents']:
            click.echo(f"   Opponents: {', '.join(recommendations['opponents'])}")
        
        click.echo(f"\n🛍️  STARTING ITEMS:")
        for item in recommendations['starting_items']:
            click.echo(f"   • {item.replace('_', ' ').title()}")
        
        click.echo(f"\n⚡ FIRST SKILL:")
        click.echo(f"   • {recommendations['first_skill'].replace('_', ' ').title()}")
        
        click.echo(f"\n🎯 EARLY GAME STRATEGY:")
        click.echo(f"   {recommendations['early_game_strategy']}")
        
        click.echo(f"\n🔧 ITEM BUILD PROGRESSION:")
        for i, item in enumerate(recommendations['item_build'], 1):
            click.echo(f"   {i}. {item.replace('_', ' ').title()}")
        
        click.echo(f"\n📊 CONFIDENCE: {recommendations['confidence']:.0%}")
        click.echo("="*60)


# Click CLI commands
@click.group()
@click.pass_context
def main(ctx):
    """DotA Coach - AI-powered coaching system for Dota 2."""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = DotACoachCLI()


@main.command()
@click.option('--hero', '-h', 
              type=click.Choice(['vengeful_spirit', 'witch_doctor', 'lich', 'lion', 'undying', 'shadow_shaman']),
              prompt='Hero name',
              help='Hero to get recommendations for')
@click.option('--lane', '-l',
              type=click.Choice(['safe', 'mid', 'off', 'jungle', 'roam']),
              prompt='Lane assignment',
              help='Lane assignment')
@click.option('--opponents', '-o',
              help='Comma-separated list of opponent heroes')
@click.pass_context
def coach(ctx, hero: str, lane: str, opponents: str):
    """Get coaching recommendations for a hero and lane matchup."""
    cli = ctx.obj['cli']
    
    # Parse opponents
    opponent_list = []
    if opponents:
        opponent_list = [opp.strip() for opp in opponents.split(',')]
    
    # Get recommendations
    recommendations = cli.simulate_coach_recommendation(hero, lane, opponent_list)
    
    # Display results
    cli.display_recommendations(recommendations)


@main.command()
@click.pass_context
def update_constants(ctx):
    """Update constants snapshots from OpenDota API."""
    cli = ctx.obj['cli']
    
    click.echo("Updating constants from OpenDota API...")
    result = cli.constants_tracker.update_constants()
    click.echo(f"Result: {result}")


@main.command()
@click.option('--patch-id', '-p',
              prompt='Patch ID',
              help='Patch ID to process data for')
@click.pass_context
def process_data(ctx, patch_id: str):
    """Process raw match data into ML-ready format."""
    cli = ctx.obj['cli']
    
    click.echo(f"Processing match data for patch {patch_id}...")
    result_path = cli.data_flattener.process_patch_data(patch_id)
    
    if result_path:
        click.echo(f"Successfully processed data: {result_path}")
    else:
        click.echo("No data was processed")


@main.command()
@click.pass_context
def status(ctx):
    """Show system status and available data."""
    cli = ctx.obj['cli']
    
    click.echo("\n" + "="*50)
    click.echo("📊 DOTA COACH SYSTEM STATUS")
    click.echo("="*50)
    
    # Check constants snapshots
    constants_dir = Path(cli.config.data_dirs['constants'])
    constants_count = len(list(constants_dir.glob('*.json')))
    click.echo(f"Constants snapshots: {constants_count}")
    
    # Check raw matches
    raw_matches_dir = Path(cli.config.data_dirs['raw_matches'])
    raw_matches_count = len(list(raw_matches_dir.glob('*.json')))
    click.echo(f"Raw matches: {raw_matches_count}")
    
    # Check processed data
    processed_dir = Path(cli.config.data_dirs['processed'])
    processed_count = len(list(processed_dir.glob('*.parquet')))
    click.echo(f"Processed datasets: {processed_count}")
    
    # Check models
    models_dir = Path(cli.config.data_dirs['models'])
    models_count = len(list(models_dir.glob('*.pkl')))
    click.echo(f"Trained models: {models_count}")
    
    click.echo("\n" + "="*50)


@main.command()
@click.option('--api-limit', '-a',
              default=1800,
              help='Maximum API calls to use in this run')
@click.option('--batch-size', '-b',
              default=50,
              help='Maximum new matches to discover per batch')
@click.option('--dry-run', '-d',
              is_flag=True,
              help='Show what would be done without making changes')
@click.pass_context
def fetch_matches_daily(ctx, api_limit: int, batch_size: int, dry_run: bool):
    """Run daily match data collection pipeline."""
    cli = ctx.obj['cli']
    
    if dry_run:
        click.echo("🔍 DRY RUN - No changes will be made")
    
    click.echo(f"\n🚀 Starting daily match data pipeline")
    click.echo(f"📊 API limit: {api_limit} calls")
    click.echo(f"📦 Batch size: {batch_size} matches")
    click.echo("="*60)
    
    try:
        # Import here to avoid circular imports
        from .match_pipeline import MatchPipeline
        
        # Create and run pipeline
        pipeline = MatchPipeline(cli.config, daily_api_limit=api_limit)
        
        if dry_run:
            # Load state and show what would be done
            if pipeline.load_state():
                click.echo(f"📋 Current state:")
                click.echo(f"   Downloaded matches: {len(pipeline.downloaded_matches)}")
                click.echo(f"   Parse backlog: {len(pipeline.parse_backlog)}")
                click.echo(f"   Would process up to {batch_size} new matches")
            else:
                click.echo("❌ Failed to load state files")
            return
        
        # Run the actual pipeline
        summary = pipeline.run_daily_pipeline(batch_size)
        
        # Display results
        click.echo(f"\n📈 PIPELINE RESULTS")
        click.echo("="*60)
        
        if summary['success']:
            click.echo(f"✅ Pipeline completed successfully")
        else:
            click.echo(f"⚠️  Pipeline completed with issues")
            if 'error' in summary:
                click.echo(f"   Error: {summary['error']}")
        
        click.echo(f"⏱️  Duration: {summary['duration_seconds']}s")
        click.echo(f"📥 Backlog processed: {summary['backlog_processed']}")
        click.echo(f"🆕 New matches processed: {summary['new_matches_processed']}")
        click.echo(f"📊 Total matches processed: {summary['total_matches_processed']}")
        click.echo(f"🌐 API calls used: {summary['api_calls_used']}/{summary['api_limit']}")
        click.echo(f"📋 Remaining in backlog: {summary['remaining_backlog']}")
        click.echo(f"💾 Total downloaded matches: {summary['total_downloaded']}")
        
        # Show API usage percentage
        api_usage_pct = (summary['api_calls_used'] / summary['api_limit']) * 100
        click.echo(f"📈 API usage: {api_usage_pct:.1f}%")
        
        if api_usage_pct > 90:
            click.echo("⚠️  Warning: High API usage!")
        
        click.echo("="*60)
        
    except Exception as e:
        click.echo(f"❌ Pipeline error: {e}")


@main.command()
@click.pass_context
def extract_topline(ctx):
    """Extract topline data from all match files to CSV."""
    cli = ctx.obj['cli']
    
    click.echo("🔄 Extracting match topline data...")
    
    try:
        # Import here to avoid circular imports
        from .extract_match_data import extract_match_topline_data
        
        # Run extraction
        stats = extract_match_topline_data(cli.config)
        
        click.echo(f"✅ Extraction complete!")
        click.echo(f"📊 Statistics:")
        click.echo(f"   - Total files processed: {stats['total_files']}")
        click.echo(f"   - Valid matches: {stats['valid_matches']}")
        click.echo(f"   - Invalid matches: {stats['invalid_matches']}")
        click.echo(f"   - Total player records: {stats['total_players']}")
        click.echo(f"   - Original rank data: {stats['players_with_original_rank']}")
        click.echo(f"   - Cleaned rank data: {stats['players_with_cleaned_rank']}")
        
    except Exception as e:
        click.echo(f"❌ Extraction error: {e}")


@main.command()
@click.option('--latest-patch', is_flag=True, help='Only analyze latest patch data')
@click.pass_context
def dashboard(ctx, latest_patch):
    """Generate ML training readiness dashboard."""
    cli = ctx.obj['cli']
    
    try:
        # Import here to avoid circular imports
        from .generate_dashboard import generate_dashboard
        
        # Generate dashboard
        dashboard_data = generate_dashboard(cli.config, latest_patch_only=latest_patch)
        
        if 'error' in dashboard_data:
            click.echo(f"❌ Dashboard error: {dashboard_data['error']}")
        else:
            # Dashboard is displayed within the generate_dashboard function
            mode_text = "latest patch only" if latest_patch else "comprehensive"
            click.echo(f"📊 Dashboard generated successfully! ({mode_text})")
            
    except Exception as e:
        click.echo(f"❌ Dashboard error: {e}")


if __name__ == '__main__':
    main()