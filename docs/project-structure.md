# Project Structure

## Overview

DotA Coach follows a modular architecture with clear separation between core functionality, data storage, documentation, and supporting systems.

## Root Directory Structure

```
DotA_Coach/
├── src/                     # Core application code
├── data/                    # All data storage and state management
├── constants/               # Game constants and patch history
├── models/                  # Trained ML models (future)
├── docs/                    # Public project documentation
├── personal_docs/           # Private development notes (gitignored)
├── tests/                   # Test suite
├── scripts/                 # Maintenance and utility scripts
├── logs/                    # Application logs
├── venv/                    # Python virtual environment (gitignored)
├── config.yaml             # Main configuration file
├── .env                    # Environment variables (gitignored)
├── requirements.txt        # Python dependencies
└── README.md              # Project overview and quick start
```

## Core Application (`src/`)

### `src/dota_coach/` - Main Package
```
src/dota_coach/
├── __init__.py             # Package initialization
├── cli.py                  # Command-line interface and user interaction
├── config.py               # Configuration management and validation
├── constants.py            # OpenDota constants tracking with metadata
├── match_pipeline.py       # Daily match collection with state management
├── extract_match_data.py   # CSV extraction with rank cleaning
├── generate_dashboard.py   # Dashboard with ML readiness assessment
├── data_flattener.py       # JSON to ML-ready format conversion (future)
├── explorer_query.py       # OpenDota Explorer API query utilities
├── hero_mapping.py         # Hero ID and name mapping utilities
├── logging_config.py       # Centralized logging configuration
└── LICENSE.md             # License information
```

### Key Module Responsibilities

#### `cli.py` - Command-Line Interface
- **Purpose**: User-facing commands for all system functionality
- **Commands Available**:
  - `coach` - Strategic coaching recommendations (placeholder logic)
  - `status` - System status and data availability
  - `update-constants` - Fetch latest game constants
  - `fetch-matches-daily` - Run daily match collection pipeline
  - `extract-topline` - Extract match data to CSV with rank cleaning
  - `dashboard` - Generate ML training readiness dashboard
  - `process-data` - Process raw match data for ML training
- **Design**: Uses Click framework for robust command parsing and help

#### `match_pipeline.py` - Data Collection Engine
- **Purpose**: Production-ready daily match data collection
- **Features**: 
  - CSV state management for deduplication across runs
  - Parse request workflow with retry logic
  - API budget tracking and enforcement
  - Hero filtering with 5x efficiency improvement
  - 4-step process: load state → process backlog → discover → save state
- **Current Status**: Operational with resolved hero filtering

#### `extract_match_data.py` - CSV Data Extraction
- **Purpose**: Process raw match JSON files into structured CSV format
- **Features**:
  - Comprehensive rank tier cleaning and validation
  - Data consistency checks and error handling
  - Structured output for analysis and ML training
  - Progress tracking during extraction
- **Current Status**: Operational, integrated with CLI

#### `generate_dashboard.py` - ML Readiness Assessment
- **Purpose**: Generate comprehensive data analysis dashboard
- **Features**:
  - Per-hero ML training readiness assessment
  - Unique player and game volume metrics
  - Training data quality analysis
  - Three-section output: overview, assessment, recommendations
- **Current Status**: Operational, provides ML training insights

#### `constants.py` - Game Constants Tracking
- **Purpose**: Enhanced patch tracking with comprehensive metadata
- **Features**:
  - Rich metadata (patch name, numeric ID, timestamps, patch date)
  - Change detection between constants snapshots
  - Comprehensive logging for debugging and monitoring
  - Meta-game focused endpoints (heroes, items, abilities, etc.)

#### `config.py` - Configuration Management
- **Purpose**: Centralized configuration loading and validation
- **Sources**: config.yaml, environment variables, CLI arguments
- **Validation**: Type checking and required field verification

## Data Storage (`data/`)

### Data Organization Strategy
```
data/
├── raw/                    # Raw data from external APIs
│   ├── matches/           # Individual match JSON files
│   │   └── 8370907704.json # Example: parsed match data (~15KB each)
│   └── public_matches/    # Basic match info from public_matches table
├── tracking/              # Pipeline state management
│   ├── downloaded_matches.csv     # Tracks successfully downloaded matches
│   ├── downloaded_matches.csv.example # Template with headers
│   ├── parse_backlog.csv         # Manages matches requiring parse requests
│   └── parse_backlog.csv.example # Template with headers
├── processed/             # ML-ready datasets (future)
│   ├── flattened/        # Structured data from raw JSON
│   ├── features/         # Engineered features for ML training
│   └── splits/           # Train/validation/test datasets
```

### State Management Design
- **CSV-Based**: Simple, transparent, debuggable state tracking
- **Deduplication**: Prevents re-downloading matches across pipeline runs
- **Retry Logic**: Manages parse requests with maximum attempt limits
- **Audit Trail**: Complete history of collection attempts and outcomes

## Game Constants (`constants/`)

### Constants Storage
```
constants/
└── snapshots/
    ├── constants_7.39_20250710_145735.json  # Enhanced metadata format
    └── [timestamp-based files for patch history]
```

### Snapshot Format
```json
{
  "timestamp": "20250710_145735",
  "patch_id": "7.39",                    # Backwards compatibility
  "patch_name": "7.39",                  # Human-readable
  "patch_numeric_id": 58,                # Numeric identifier
  "datetime_captured": "2025-07-10T14:56:15+00:00",
  "patch_date": "2025-05-22T23:36:01.602Z",
  "constants": { ... }                   # Actual constants data
}
```

## Documentation (`docs/` vs `personal_docs/`)

### Public Documentation (`docs/`)
- **Purpose**: Open source project documentation for users and contributors
- **Files**:
  - `architecture.md` - Technical system design and 5-phase vision
  - `getting-started.md` - Detailed setup, usage, and troubleshooting
  - `development-roadmap.md` - Current tasks, priorities, and progress
  - `project-structure.md` - Codebase organization (this file)
- **Audience**: External users, potential contributors, future developers

### Private Documentation (`personal_docs/`)
- **Purpose**: Private development notes and decision history
- **Files**:
  - `PLANNING.md` - Complete project vision and architecture decisions
  - `TASKS.md` - Detailed development roadmap with task breakdown
  - `WorkSessionNotes.md` - Historical development decisions and learnings
  - `QuickCatchUp.md` - Current status snapshot for AI assistant context
- **Audience**: Project owner and AI development assistant
- **Git Status**: Excluded from version control (gitignored)

## Configuration Files

### `config.yaml` - Main Configuration
```yaml
api:
  opendota:
    base_url: "https://api.opendota.com/api"
    rate_limit_per_minute: 60

data_collection:
  hero_ids: [20, 26, 27, 30, 31, 85]  # MVP support heroes
  daily_api_limit: 1800
  batch_size: 50

constants:
  endpoints: ["heroes", "items", "abilities", "permanent_buffs", "xp_level", "skillshots"]
```

### `.env` - Environment Variables
```bash
OPENDOTA_API_KEY=your_api_key_here
LOG_LEVEL=INFO
LOG_FILE=logs/dota_coach.log
DATA_DIR=data
CONSTANTS_DIR=constants
MODELS_DIR=models
```

## Future Directories

### `models/` - ML Model Storage (Future - Phase 1)
```
models/
├── item_recommendations/   # Item purchase prediction models
├── skill_timing/          # Skill upgrade timing models
├── positioning/           # Aggressive/defensive classification
└── metadata/             # Model versioning and performance metrics
```

### `tests/` - Test Suite
```
tests/
├── unit/                  # Unit tests for individual modules
├── integration/           # Integration tests for component interaction
├── fixtures/             # Test data and mock responses
└── performance/          # Performance benchmarks and load tests
```

## Development Support

### `scripts/` - Utility Scripts
```
scripts/
├── daily_constants_update.py  # Legacy constants update script
└── temp/                      # Temporary development scripts
    └── extract_match.py       # Match data analysis utilities
```

### `logs/` - Application Logs
```
logs/
├── dota_coach.log            # Main application log
├── dota_coach.log.1          # Rotated log files
└── [automatic rotation at 10MB]
```

## Design Principles

### Modularity
- **Clear Separation**: ML brain vs interface layers independent
- **Single Responsibility**: Each module has focused, well-defined purpose
- **Loose Coupling**: Minimal dependencies between components
- **Interface Consistency**: Standardized APIs between modules

### Scalability
- **Data Organization**: Supports growth from MB to GB scale
- **State Management**: Handles thousands of matches efficiently
- **Configuration**: Easily adjustable for different environments
- **Future Extensions**: Architecture supports additional heroes, game modes

### Maintainability  
- **Transparent State**: CSV files provide clear audit trail
- **Comprehensive Logging**: Detailed operation tracking for debugging
- **Documentation**: Both public and private documentation maintained
- **Version Control**: Proper gitignore for sensitive/generated files

### Development Workflow
- **Phase-Gated**: Clear boundaries between development phases
- **Testing**: Structure supports comprehensive test coverage
- **Documentation**: Real-time updates with development progress
- **Quality Standards**: Consistent code organization and standards

---

*This structure supports systematic development from current data collection through future ML training and multi-modal interface implementation, maintaining clear organization and separation of concerns throughout the development process.*