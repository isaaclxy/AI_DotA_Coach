# DotA Coach Dashboard Generation Module
# Generates ML training readiness dashboard from topline match data CSV
# Focuses on per-hero analysis for strategic decision making

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

from .config import Config
from .hero_mapping import HeroMapper


class DashboardGenerator:
    """Generates ML training readiness dashboard from topline data."""
    
    def __init__(self, config: Config, filter_latest_patch_only: bool = False):
        """
        Initialize dashboard generator.
        
        Args:
            config (Config): Configuration manager instance.
            filter_latest_patch_only (bool): If True, only analyze latest patch data.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.hero_mapper = HeroMapper()
        self.filter_latest_patch_only = filter_latest_patch_only
        
        # Set up paths
        self.csv_path = Path(config.data_dirs['tracking']) / "match_topline_data.csv"
        
        # Target hero IDs (support heroes)
        self.target_hero_ids = [20, 30, 31, 26, 85, 28]  # VS, WD, Lich, Lion, Undying, SS
        
        # Skill tier thresholds
        self.skill_tiers = {
            'Divine+': 80,
            'Ancient': 70,
            'Legend': 60,
            'Archon': 50,
            'Lower': 0
        }
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """
        Generate comprehensive ML training dashboard.
        
        Returns:
            Dict[str, Any]: Dashboard data and statistics.
        """
        self.logger.info("Generating ML training dashboard...")
        
        # If instance is configured for latest patch only, generate single dashboard
        if self.filter_latest_patch_only:
            return self._generate_single_dashboard(latest_patch_only=True)
        
        # Otherwise, generate comprehensive dashboard with both all data and latest patch
        return self._generate_comprehensive_dashboard()
    
    def _generate_single_dashboard(self, latest_patch_only: bool = False) -> Dict[str, Any]:
        """
        Generate single dashboard (either all data or latest patch only).
        
        Args:
            latest_patch_only (bool): If True, filter to latest patch only.
            
        Returns:
            Dict[str, Any]: Dashboard data and statistics.
        """
        # Load data
        df = self._load_data(latest_patch_only=latest_patch_only)
        if df is None:
            return {'error': 'Failed to load topline data'}
        
        # Generate dashboard sections
        dashboard_data = {
            'data_overview': self._generate_data_overview(df),
            'hero_coverage': self._generate_hero_coverage(df),
            'hero_matchups': self._generate_hero_matchups(df),
            'per_hero_assessment': self._generate_per_hero_assessment(df),
            'recommendations': self._generate_recommendations(df),
            'latest_patch_only': latest_patch_only
        }
        
        # Display dashboard
        self._display_dashboard(dashboard_data)
        
        return dashboard_data
    
    def _generate_comprehensive_dashboard(self) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard with both all data and latest patch analysis.
        
        Returns:
            Dict[str, Any]: Dashboard data and statistics.
        """
        # Load all data first to get patch information
        df_all = self._load_data(latest_patch_only=False)
        if df_all is None:
            return {'error': 'Failed to load topline data'}
        
        # Check if we have multiple patches
        patch_distribution = self._get_patch_distribution(df_all)
        if len(patch_distribution) == 1:
            # Only one patch, no need for separation
            return self._generate_single_dashboard(latest_patch_only=False)
        
        # Generate all data analysis
        all_data_analysis = {
            'data_overview': self._generate_data_overview(df_all),
            'hero_coverage': self._generate_hero_coverage(df_all),
            'hero_matchups': self._generate_hero_matchups(df_all),
            'per_hero_assessment': self._generate_per_hero_assessment(df_all),
            'recommendations': self._generate_recommendations(df_all)
        }
        
        # Load latest patch data
        df_latest = self._load_data(latest_patch_only=True)
        if df_latest is None or len(df_latest) == 0:
            # No latest patch data, return all data only
            dashboard_data = {
                'all_data': all_data_analysis,
                'latest_patch': None,
                'mode': 'all_data_only'
            }
        else:
            # Generate latest patch analysis
            latest_patch_analysis = {
                'data_overview': self._generate_data_overview(df_latest),
                'hero_coverage': self._generate_hero_coverage(df_latest),
                'hero_matchups': self._generate_hero_matchups(df_latest),
                'per_hero_assessment': self._generate_per_hero_assessment(df_latest),
                'recommendations': self._generate_recommendations(df_latest)
            }
            
            dashboard_data = {
                'all_data': all_data_analysis,
                'latest_patch': latest_patch_analysis,
                'mode': 'comprehensive'
            }
        
        # Display comprehensive dashboard
        self._display_comprehensive_dashboard(dashboard_data)
        
        return dashboard_data
    
    def _detect_latest_patch(self, df: pd.DataFrame) -> int:
        """
        Detect the latest patch number in the dataset.
        
        Args:
            df (pd.DataFrame): The loaded data.
            
        Returns:
            int: Latest patch number.
        """
        return df['patch'].max()
    
    def _get_patch_distribution(self, df: pd.DataFrame) -> Dict[int, int]:
        """
        Get patch distribution in the dataset.
        
        Args:
            df (pd.DataFrame): The loaded data.
            
        Returns:
            Dict[int, int]: Patch number to match count mapping.
        """
        return df.groupby('patch')['match_id'].nunique().to_dict()
    
    def _load_data(self, latest_patch_only: bool = None) -> Optional[pd.DataFrame]:
        """
        Load topline data from CSV file with optional patch filtering.
        
        Args:
            latest_patch_only (bool, optional): Override instance setting for patch filtering.
        
        Returns:
            Optional[pd.DataFrame]: Loaded data or None if error.
        """
        if not self.csv_path.exists():
            self.logger.error(f"Topline data not found at {self.csv_path}")
            print(f"❌ Error: Topline data not found at {self.csv_path}")
            print("💡 Run 'python -m src.dota_coach.cli extract-topline' first")
            return None
        
        try:
            df = pd.read_csv(self.csv_path)
            
            # Validate required columns
            required_columns = [
                'match_id', 'hero_id', 'player_rank_tier_cleaned', 
                'lobby_type', 'patch', 'source'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    self.logger.error(f"Missing required column: {col}")
                    return None
            
            # Apply patch filtering if requested
            filter_patch = latest_patch_only if latest_patch_only is not None else self.filter_latest_patch_only
            if filter_patch:
                latest_patch = self._detect_latest_patch(df)
                df = df[df['patch'] == latest_patch]
                self.logger.info(f"Filtered to latest patch {latest_patch}: {len(df)} players")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading CSV: {e}")
            return None
    
    def _generate_data_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data overview statistics."""
        total_players = len(df)
        total_matches = df['match_id'].nunique()
        
        # Count original vs cleaned ranks
        original_rank_count = df['player_rank_tier'].notna().sum()
        cleaned_rank_count = df['player_rank_tier_cleaned'].notna().sum()
        
        # Source breakdown
        source_counts = df['source'].value_counts().to_dict()
        
        # Patch distribution
        patch_distribution = self._get_patch_distribution(df)
        latest_patch = self._detect_latest_patch(df) if len(df) > 0 else None
        
        return {
            'total_matches': total_matches,
            'total_players': total_players,
            'original_rank_count': original_rank_count,
            'cleaned_rank_count': cleaned_rank_count,
            'source_breakdown': source_counts,
            'patch_distribution': patch_distribution,
            'latest_patch': latest_patch
        }
    
    def _generate_hero_coverage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate hero coverage statistics."""
        hero_counts = df['hero_id'].value_counts()
        
        # Target hero coverage with unique players and games
        target_coverage = {}
        for hero_id in self.target_hero_ids:
            hero_name = self.hero_mapper.id_to_name(hero_id)
            if hero_name:
                display_name = self.hero_mapper.get_display_name(hero_name)
                hero_df = df[df['hero_id'] == hero_id]
                
                unique_players = hero_df['account_id'].nunique()
                total_games = len(hero_df)
                
                target_coverage[hero_id] = {
                    'name': display_name,
                    'unique_players': unique_players,
                    'total_games': total_games
                }
        
        return {
            'total_unique_heroes': len(hero_counts),
            'target_hero_coverage': target_coverage,
            'all_hero_counts': hero_counts.to_dict()
        }
    
    def _generate_skill_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate skill tier distribution."""
        # Use cleaned rank data
        ranked_df = df[df['player_rank_tier_cleaned'].notna()]
        
        skill_distribution = {}
        for tier_name, min_rank in self.skill_tiers.items():
            if tier_name == 'Lower':
                count = len(ranked_df[ranked_df['player_rank_tier_cleaned'] < 50])
            else:
                next_tier_min = self.skill_tiers.get(list(self.skill_tiers.keys())[list(self.skill_tiers.keys()).index(tier_name) - 1], 999)
                count = len(ranked_df[
                    (ranked_df['player_rank_tier_cleaned'] >= min_rank) & 
                    (ranked_df['player_rank_tier_cleaned'] < next_tier_min)
                ])
            
            skill_distribution[tier_name] = {
                'count': count,
                'percentage': (count / len(ranked_df) * 100) if len(ranked_df) > 0 else 0
            }
        
        return {
            'total_ranked_players': len(ranked_df),
            'skill_distribution': skill_distribution
        }
    
    def _generate_hero_matchups(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate hero matchup analysis."""
        matchups = defaultdict(int)
        
        # Group by match and count hero pairings
        for match_id in df['match_id'].unique():
            match_heroes = df[df['match_id'] == match_id]['hero_id'].values
            
            # Count pairwise encounters
            for i, hero1 in enumerate(match_heroes):
                for hero2 in match_heroes[i+1:]:
                    # Only count if both are target heroes
                    if hero1 in self.target_hero_ids and hero2 in self.target_hero_ids:
                        pair = tuple(sorted([hero1, hero2]))
                        matchups[pair] += 1
        
        # Convert to readable format
        readable_matchups = {}
        for (hero1, hero2), count in matchups.items():
            hero1_name = self.hero_mapper.get_display_name(self.hero_mapper.id_to_name(hero1))
            hero2_name = self.hero_mapper.get_display_name(self.hero_mapper.id_to_name(hero2))
            readable_matchups[f"{hero1_name} vs {hero2_name}"] = count
        
        # Sort by frequency
        sorted_matchups = dict(sorted(readable_matchups.items(), key=lambda x: x[1], reverse=True))
        
        return {
            'total_matchups': len(matchups),
            'matchup_counts': sorted_matchups,
            'most_common': list(sorted_matchups.items())[:5],
            'least_common': list(sorted_matchups.items())[-5:]
        }
    
    def _generate_per_hero_assessment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate per-hero ML training assessment."""
        assessments = {}
        
        for hero_id in self.target_hero_ids:
            hero_name = self.hero_mapper.id_to_name(hero_id)
            display_name = self.hero_mapper.get_display_name(hero_name)
            
            # Filter data for this hero
            hero_df = df[df['hero_id'] == hero_id]
            
            if len(hero_df) == 0:
                assessments[hero_id] = {
                    'name': display_name,
                    'unique_players': 0,
                    'total_games': 0,
                    'data_volume': {'status': '❌', 'rating': 'NO DATA'},
                    'skill_quality': {'status': '❌', 'high_skill_pct': 0, 'rating': 'NO DATA'},
                    'matchup_diversity': {'status': '❌', 'unique_opponents': 0, 'rating': 'NO DATA'}
                }
                continue
            
            # Calculate unique players and total games
            unique_players = hero_df['account_id'].nunique()
            total_games = len(hero_df)
            
            # Data volume assessment based on unique players
            if unique_players >= 100:
                volume_status = '✅'
                volume_rating = 'EXCELLENT'
            elif unique_players >= 50:
                volume_status = '✅'
                volume_rating = 'GOOD'
            elif unique_players >= 25:
                volume_status = '⚠️'
                volume_rating = 'MODERATE'
            else:
                volume_status = '❌'
                volume_rating = 'INSUFFICIENT'
            
            # Skill quality assessment
            ranked_hero_df = hero_df[hero_df['player_rank_tier_cleaned'].notna()]
            if len(ranked_hero_df) > 0:
                high_skill_count = len(ranked_hero_df[ranked_hero_df['player_rank_tier_cleaned'] >= 70])
                high_skill_pct = (high_skill_count / len(ranked_hero_df)) * 100
                
                if high_skill_pct >= 65:
                    skill_status = '✅'
                    skill_rating = 'EXCELLENT'
                elif high_skill_pct >= 50:
                    skill_status = '✅'
                    skill_rating = 'GOOD'
                elif high_skill_pct >= 35:
                    skill_status = '⚠️'
                    skill_rating = 'MODERATE'
                else:
                    skill_status = '❌'
                    skill_rating = 'LOW'
            else:
                high_skill_pct = 0
                skill_status = '❌'
                skill_rating = 'NO RANK DATA'
            
            # Matchup diversity assessment
            hero_matches = hero_df['match_id'].unique()
            opponents = set()
            for match_id in hero_matches:
                match_heroes = df[df['match_id'] == match_id]['hero_id'].values
                opponents.update(h for h in match_heroes if h != hero_id)
            
            unique_opponents = len(opponents)
            if unique_opponents >= 40:
                diversity_status = '✅'
                diversity_rating = 'EXCELLENT'
            elif unique_opponents >= 25:
                diversity_status = '✅'
                diversity_rating = 'GOOD'
            elif unique_opponents >= 15:
                diversity_status = '⚠️'
                diversity_rating = 'MODERATE'
            else:
                diversity_status = '❌'
                diversity_rating = 'LIMITED'
            
            assessments[hero_id] = {
                'name': display_name,
                'unique_players': unique_players,
                'total_games': total_games,
                'data_volume': {
                    'status': volume_status,
                    'rating': volume_rating
                },
                'skill_quality': {
                    'status': skill_status,
                    'high_skill_pct': high_skill_pct,
                    'rating': skill_rating
                },
                'matchup_diversity': {
                    'status': diversity_status,
                    'unique_opponents': unique_opponents,
                    'rating': diversity_rating
                }
            }
        
        return assessments
    
    def _generate_recommendations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate ML training recommendations."""
        per_hero = self._generate_per_hero_assessment(df)
        
        ready_heroes = []
        needs_more_data = []
        collect_more = []
        
        for hero_id, assessment in per_hero.items():
            hero_name = assessment['name']
            
            # Check if hero is ready (all green or mostly green)
            volume_good = assessment['data_volume']['status'] == '✅'
            skill_good = assessment['skill_quality']['status'] in ['✅', '⚠️']
            diversity_good = assessment['matchup_diversity']['status'] in ['✅', '⚠️']
            
            if volume_good and skill_good and diversity_good:
                ready_heroes.append(hero_name)
            elif assessment['unique_players'] >= 25:
                needs_more_data.append(hero_name)
            else:
                collect_more.append(hero_name)
        
        # Overall recommendation
        if len(ready_heroes) >= 3:
            overall_recommendation = "PROCEED with selective training"
        elif len(ready_heroes) >= 1:
            overall_recommendation = "PROCEED with limited training"
        else:
            overall_recommendation = "CONTINUE data collection"
        
        return {
            'overall_recommendation': overall_recommendation,
            'ready_heroes': ready_heroes,
            'needs_more_data': needs_more_data,
            'collect_more': collect_more
        }
    
    def _display_dashboard(self, data: Dict[str, Any]) -> None:
        """Display formatted dashboard to console."""
        patch_filter_text = " (LATEST PATCH ONLY)" if data.get('latest_patch_only', False) else ""
        
        print("\n" + "="*60)
        print(f"📊 AI DOTA COACH DATA DASHBOARD{patch_filter_text}")
        print("="*60)
        
        # Data Overview
        overview = data['data_overview']
        print(f"\n📈 Data Collection Summary:")
        print(f"  Total Matches: {overview['total_matches']}")
        print(f"  Total Players: {overview['total_players']}")
        print(f"  Data Sources: {dict(overview['source_breakdown'])}")
        
        # Patch information
        if 'patch_distribution' in overview and overview['patch_distribution']:
            patch_dist = overview['patch_distribution']
            latest_patch = overview.get('latest_patch')
            print(f"  Patch Distribution: {dict(patch_dist)}")
            if latest_patch:
                print(f"  Latest Patch: {latest_patch}")
        
        print(f"  Players with Original Rank: {overview['original_rank_count']} ({overview['original_rank_count']/overview['total_players']*100:.1f}%)")
        print(f"  Players with Cleaned Rank: {overview['cleaned_rank_count']} ({overview['cleaned_rank_count']/overview['total_players']*100:.1f}%)")
        
        # Per-Hero Assessment
        print(f"\n✅ ML Training Readiness (Per Hero):")
        print("")
        assessments = data['per_hero_assessment']
        for hero_id in self.target_hero_ids:
            assessment = assessments[hero_id]
            print(f"{assessment['name'].upper()} (ID: {hero_id})")
            print(f"  Data Volume: {assessment['data_volume']['status']} {assessment['unique_players']} unique players across {assessment['total_games']} games ({assessment['data_volume']['rating']})")
            print(f"  Skill Quality: {assessment['skill_quality']['status']} {assessment['skill_quality']['high_skill_pct']:.1f}% high-skill Ancient+ ({assessment['skill_quality']['rating']})")
            print(f"  Matchup Diversity: {assessment['matchup_diversity']['status']} {assessment['matchup_diversity']['unique_opponents']} unique opponent heroes ({assessment['matchup_diversity']['rating']})")
            print("")
        
        # Recommendations
        recommendations = data['recommendations']
        print(f"📋 RECOMMENDATION: {recommendations['overall_recommendation']}")
        
        if recommendations['ready_heroes']:
            print(f"- READY NOW: {', '.join(recommendations['ready_heroes'])}")
        
        if recommendations['needs_more_data']:
            print(f"- NEEDS MORE DATA: {', '.join(recommendations['needs_more_data'])}")
        
        if recommendations['collect_more']:
            print(f"- COLLECT MORE: {', '.join(recommendations['collect_more'])}")
        
        print("\n" + "="*60)
    
    def _display_comprehensive_dashboard(self, data: Dict[str, Any]) -> None:
        """Display comprehensive dashboard with both all data and latest patch analysis."""
        print("\n" + "="*80)
        print("📊 AI DOTA COACH COMPREHENSIVE DATA DASHBOARD")
        print("="*80)
        
        if data['mode'] == 'all_data_only':
            print("\n⚠️ Only one patch detected - showing all data analysis")
            self._display_single_section("📊 ALL DATA ANALYSIS", data['all_data'])
        else:
            # Display all data section
            print("\n" + "="*80)
            print("📊 ALL DATA ANALYSIS")
            print("="*80)
            self._display_section_content(data['all_data'])
            
            # Display latest patch section
            if data['latest_patch']:
                latest_patch_num = data['latest_patch']['data_overview']['latest_patch']
                print("\n" + "="*80)
                print(f"🚀 LATEST PATCH ({latest_patch_num}) ANALYSIS")
                print("="*80)
                self._display_section_content(data['latest_patch'])
    
    def _display_single_section(self, title: str, section_data: Dict[str, Any]) -> None:
        """Display a single section with title."""
        print(f"\n{title}")
        print("="*len(title))
        self._display_section_content(section_data)
    
    def _display_section_content(self, data: Dict[str, Any]) -> None:
        """Display the content of a dashboard section."""
        # Data Overview
        overview = data['data_overview']
        print(f"\n📈 Data Collection Summary:")
        print(f"  Total Matches: {overview['total_matches']}")
        print(f"  Total Players: {overview['total_players']}")
        print(f"  Data Sources: {dict(overview['source_breakdown'])}")
        
        # Patch information
        if 'patch_distribution' in overview and overview['patch_distribution']:
            patch_dist = overview['patch_distribution']
            latest_patch = overview.get('latest_patch')
            print(f"  Patch Distribution: {dict(patch_dist)}")
            if latest_patch:
                print(f"  Latest Patch: {latest_patch}")
        
        print(f"  Players with Original Rank: {overview['original_rank_count']} ({overview['original_rank_count']/overview['total_players']*100:.1f}%)")
        print(f"  Players with Cleaned Rank: {overview['cleaned_rank_count']} ({overview['cleaned_rank_count']/overview['total_players']*100:.1f}%)")
        
        # Per-Hero Assessment
        print(f"\n✅ ML Training Readiness (Per Hero):")
        print("")
        assessments = data['per_hero_assessment']
        for hero_id in self.target_hero_ids:
            assessment = assessments[hero_id]
            print(f"{assessment['name'].upper()} (ID: {hero_id})")
            print(f"  Data Volume: {assessment['data_volume']['status']} {assessment['unique_players']} unique players across {assessment['total_games']} games ({assessment['data_volume']['rating']})")
            print(f"  Skill Quality: {assessment['skill_quality']['status']} {assessment['skill_quality']['high_skill_pct']:.1f}% high-skill Ancient+ ({assessment['skill_quality']['rating']})")
            print(f"  Matchup Diversity: {assessment['matchup_diversity']['status']} {assessment['matchup_diversity']['unique_opponents']} unique opponent heroes ({assessment['matchup_diversity']['rating']})")
            print("")
        
        # Recommendations
        recommendations = data['recommendations']
        print(f"📋 RECOMMENDATION: {recommendations['overall_recommendation']}")
        
        if recommendations['ready_heroes']:
            print(f"- READY NOW: {', '.join(recommendations['ready_heroes'])}")
        
        if recommendations['needs_more_data']:
            print(f"- NEEDS MORE DATA: {', '.join(recommendations['needs_more_data'])}")
        
        if recommendations['collect_more']:
            print(f"- COLLECT MORE: {', '.join(recommendations['collect_more'])}")
        
        print("\n" + "="*40)


def generate_dashboard(config: Config = None, latest_patch_only: bool = False) -> Dict[str, Any]:
    """
    Generate ML training dashboard from topline data.
    
    Args:
        config (Config, optional): Configuration instance.
        latest_patch_only (bool): If True, only analyze latest patch data.
        
    Returns:
        Dict[str, Any]: Dashboard data.
    """
    if config is None:
        config = Config()
    
    generator = DashboardGenerator(config, filter_latest_patch_only=latest_patch_only)
    return generator.generate_dashboard()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Generate dashboard
    dashboard_data = generate_dashboard()