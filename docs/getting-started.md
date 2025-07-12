# Getting Started Guide

## System Requirements

### Prerequisites
- **Python 3.12+** (required for modern type hints and performance)
- **OpenDota API Key** (free registration at [OpenDota](https://www.opendota.com/api-keys))
- **Git** (for repository management)
- **4GB+ RAM** (for data processing and future ML training)
- **10GB+ Storage** (for match data collection)

### Operating System Support
- **macOS** (primary development environment)
- **Linux** (Ubuntu 20.04+, other distributions)
- **Windows** (with WSL recommended for best experience)

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd DotA_Coach
```

### 2. Python Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate          # macOS/Linux
# OR
venv\\Scripts\\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env  # or your preferred editor
```

**Required .env Configuration:**
```bash
OPENDOTA_API_KEY=your_api_key_here
LOG_LEVEL=INFO
LOG_FILE=logs/dota_coach.log
DATA_DIR=data
CONSTANTS_DIR=constants
MODELS_DIR=models
```

### 5. Verify Installation
```bash
python -m src.dota_coach.cli status
```

**Expected Output:**
```
==================================================
📊 DOTA COACH SYSTEM STATUS
==================================================
Constants snapshots: X
Raw matches: X
Processed datasets: 0
Trained models: 0
==================================================
```

## Basic Usage

### System Status and Information
```bash
# Check overall system status
python -m src.dota_coach.cli status

# View available CLI commands
python -m src.dota_coach.cli --help
```

### Data Collection

#### Update Game Constants
```bash
# Fetch latest patch constants from OpenDota
python -m src.dota_coach.cli update-constants
```

#### Collect Match Data
```bash
# Run daily match collection (with API limits)
python -m src.dota_coach.cli fetch-matches-daily --api-limit 1800 --batch-size 50

# Dry run to see what would be collected
python -m src.dota_coach.cli fetch-matches-daily --dry-run

# Small test collection
python -m src.dota_coach.cli fetch-matches-daily --api-limit 50 --batch-size 10
```

### Strategic Coaching (Current - Placeholder Logic)
```bash
# Get coaching recommendations for specific hero/lane
python -m src.dota_coach.cli coach --hero vengeful_spirit --lane safe

# Include opponent information
python -m src.dota_coach.cli coach --hero witch_doctor --lane safe --opponents pudge,invoker
```

**Available Heroes (MVP):**
- `vengeful_spirit`
- `witch_doctor`
- `lich`
- `lion`
- `undying`
- `shadow_shaman`

**Available Lanes:**
- `safe` (safe lane)
- `mid` (middle lane)
- `off` (off lane)
- `jungle`
- `roam`

## Understanding the Data Pipeline

### State Management
The system uses CSV files to track data collection progress:
- **`data/state/downloaded_matches.csv`**: Tracks successfully downloaded matches
- **`data/state/parse_backlog.csv`**: Manages matches requiring parse requests

### Data Organization
```
data/
├── raw/matches/              # Raw match JSON files
│   └── 8370907704.json      # Individual match files
├── state/                   # Pipeline state tracking
│   ├── downloaded_matches.csv
│   └── parse_backlog.csv
└── processed/               # ML-ready datasets (future)
```

### Match Collection Workflow
1. **Discovery**: Find new matches via OpenDota Explorer API
2. **Download**: Fetch individual match details
3. **Parse Requests**: Queue unparsed matches for processing
4. **State Tracking**: Maintain CSV records for deduplication

## Configuration Details

### config.yaml Structure
```yaml
api:
  opendota:
    base_url: "https://api.opendota.com/api"
    rate_limit_per_minute: 60
    
data_collection:
  hero_ids: [20, 26, 27, 30, 31, 85]  # MVP support heroes
  patch_filter: true
  min_rank_tier: 70  # High-skill matches only
  
constants:
  endpoints:
    - "heroes"
    - "items"
    - "abilities"
    - "permanent_buffs"
    - "xp_level"
    - "skillshots"
```

### Logging Configuration
- **Log Location**: `logs/dota_coach.log`
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Rotation**: Automatic log rotation at 10MB

## Troubleshooting

### Common Issues

#### "No API key found"
**Solution**: Ensure `.env` file exists with valid `OPENDOTA_API_KEY`
```bash
# Check if .env exists
ls -la .env

# Verify API key format (should be string, no quotes needed in .env)
cat .env | grep OPENDOTA_API_KEY
```

#### "Module not found" errors
**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
# Check if venv is active (should show (venv) in prompt)
which python

# Reinstall dependencies if needed
pip install -r requirements.txt
```

#### "API rate limit exceeded"
**Solution**: Reduce API usage or wait for limit reset
```bash
# Use smaller batch sizes
python -m src.dota_coach.cli fetch-matches-daily --api-limit 100 --batch-size 10

# Check current API usage in logs
tail -f logs/dota_coach.log
```

#### "No matches found" during collection
**Current Known Issue**: Hero filtering optimization in progress
- **Status**: Complex queries cause OpenDota API timeouts
- **Workaround**: System collects all high-rank matches, filters later
- **Solution**: Phase 1 blocker - alternative query patterns being researched

### Performance Tips

#### Optimize Data Collection
```bash
# Monitor API usage during collection
python -m src.dota_coach.cli fetch-matches-daily --api-limit 1800 --batch-size 50

# Use dry-run to estimate collection time
python -m src.dota_coach.cli fetch-matches-daily --dry-run --batch-size 100
```

#### Storage Management
- **Raw matches**: ~15KB per match
- **Daily collection**: ~250-400MB for 1800 API calls
- **Clean old logs**: `logs/` directory grows over time

## Next Steps

### Current Development Focus (Phase 1)
1. **Hero Filtering Optimization**: Resolve API query timeouts
2. **Data Flattening**: Convert raw JSON to ML-ready format
3. **ML Model Training**: Train strategic decision models
4. **Enhanced CLI**: Replace placeholder logic with ML recommendations

### Development Environment Setup
```bash
# Install development dependencies
pip install pytest ruff mypy

# Run tests
pytest tests/

# Run linting
ruff check src/

# Type checking
mypy src/
```

### Contributing to Development
1. **Understand Current Phase**: Review [Development Roadmap](development-roadmap.md)
2. **Check Project Structure**: Review [Project Structure](project-structure.md)
3. **Follow Architecture**: Review [System Architecture](architecture.md)
4. **Test Changes**: Ensure all tests pass before submitting

## Support

### Getting Help
1. **Check Logs**: Most issues show detailed information in `logs/dota_coach.log`
2. **System Status**: Run `python -m src.dota_coach.cli status` for current state
3. **Documentation**: Review architecture and roadmap documents
4. **Create Issue**: Report bugs or request features in repository

### Development Community
- **Phase-gated Development**: No advancement until current phase complete
- **Outcome-focused Tasks**: Each task represents 2-3 hours focused work
- **Quality Standards**: Comprehensive testing and documentation required

---

*This guide provides everything needed to set up and start using DotA Coach. The system is currently in Phase 1 development, focusing on building the foundational ML model capabilities.*