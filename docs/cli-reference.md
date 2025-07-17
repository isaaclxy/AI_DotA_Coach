# CLI Reference - DotA Coach

Complete reference for all command-line interface commands available in the DotA Coach system.

## Quick Reference

```bash
# Core Commands
python -m src.dota_coach.cli status                    # System status
python -m src.dota_coach.cli update-constants          # Update game constants
python -m src.dota_coach.cli fetch-matches-daily       # Daily match collection
python -m src.dota_coach.cli extract-topline           # Extract match data to CSV
python -m src.dota_coach.cli dashboard                 # Generate ML readiness dashboard

# Analysis & Coaching
python -m src.dota_coach.cli coach --hero vengeful_spirit --lane safe
python -m src.dota_coach.cli process-data              # Process raw data for ML
```

## Commands

### `status`
**Purpose**: Display system status and available data.

```bash
python -m src.dota_coach.cli status
```

**Output**:
- Constants snapshots available
- Match data statistics
- Data storage location
- System configuration status

**Example**:
```bash
python -m src.dota_coach.cli status
```

---

### `update-constants`
**Purpose**: Update game constants from OpenDota API.

```bash
python -m src.dota_coach.cli update-constants
```

**Features**:
- Fetches latest patch constants (heroes, items, abilities)
- Only updates when changes detected
- Maintains historical snapshots
- Rich metadata tracking

**Example**:
```bash
python -m src.dota_coach.cli update-constants
```

---

### `fetch-matches-daily`
**Purpose**: Run daily match data collection pipeline.

```bash
python -m src.dota_coach.cli fetch-matches-daily [OPTIONS]
```

**Options**:
- `--api-limit INTEGER`: Maximum API calls per day (default: 1800)
- `--batch-size INTEGER`: Matches to discover per batch (default: 50)
- `--dry-run`: Show what would be collected without making changes
- `--help`: Show command help

**Features**:
- Targeted hero filtering (7 support heroes)
- CSV state management with deduplication
- Parse request workflow with retry logic
- Rate limiting and API budget control
- External drive support

**Examples**:
```bash
# Standard daily collection
python -m src.dota_coach.cli fetch-matches-daily

# Custom limits for testing
python -m src.dota_coach.cli fetch-matches-daily --api-limit 100 --batch-size 10

# Dry run to preview collection
python -m src.dota_coach.cli fetch-matches-daily --dry-run
```

---

### `extract-topline`
**Purpose**: Extract match data to CSV with rank cleaning.

```bash
python -m src.dota_coach.cli extract-topline
```

**Features**:
- Processes all raw match JSON files
- Comprehensive rank tier cleaning
- Data validation and consistency checks
- Structured CSV output for analysis
- Progress tracking during extraction

**Output**: Creates CSV file with cleaned match data ready for analysis.

**Example**:
```bash
python -m src.dota_coach.cli extract-topline
```

---

### `dashboard`
**Purpose**: Generate ML training readiness dashboard.

```bash
python -m src.dota_coach.cli dashboard
```

**Features**:
- Per-hero ML readiness assessment
- Unique player and game volume metrics
- Training data quality analysis
- Actionable recommendations for ML development
- Three-section output: overview, assessment, recommendations

**Output**: Comprehensive dashboard showing ML training readiness by hero.

**Example**:
```bash
python -m src.dota_coach.cli dashboard
```

---

### `coach`
**Purpose**: Get coaching recommendations for a hero and lane.

```bash
python -m src.dota_coach.cli coach --hero HERO --lane LANE [OPTIONS]
```

**Options**:
- `--hero TEXT`: Hero name (required)
- `--lane TEXT`: Lane assignment (required)
- `--opponents TEXT`: Comma-separated opponent heroes
- `--help`: Show command help

**Available Heroes**:
- `vengeful_spirit`
- `witch_doctor`
- `lich`
- `lion`
- `undying`
- `shadow_shaman`

**Available Lanes**:
- `safe` (safe lane)
- `mid` (middle lane)
- `off` (off lane)
- `jungle`
- `roam`

**Examples**:
```bash
# Basic coaching
python -m src.dota_coach.cli coach --hero vengeful_spirit --lane safe

# With opponent information
python -m src.dota_coach.cli coach --hero witch_doctor --lane safe --opponents pudge,invoker
```

---

### `process-data`
**Purpose**: Process raw match data into ML-ready format.

```bash
python -m src.dota_coach.cli process-data
```

**Features**:
- Converts raw JSON to ML training format
- Feature engineering for strategic decisions
- Data preprocessing and normalization
- Validation of processed datasets

**Example**:
```bash
python -m src.dota_coach.cli process-data
```

## Data Analysis Workflow

### 1. Collection Phase
```bash
# Daily match collection
python -m src.dota_coach.cli fetch-matches-daily --api-limit 1800 --batch-size 50
```

### 2. Extraction Phase
```bash
# Extract to CSV
python -m src.dota_coach.cli extract-topline
```

### 3. Analysis Phase
```bash
# Generate dashboard
python -m src.dota_coach.cli dashboard
```

### 4. Training Phase
```bash
# Process for ML
python -m src.dota_coach.cli process-data
```

## External Drive Configuration

For large-scale data collection, configure external drive storage:

```bash
# 1. Copy example configuration
cp data/.data_location.example data/.data_location

# 2. Edit with your external drive path
# Example: /Volumes/ExternalDrive/DotA_Coach_Data

# 3. All commands automatically use external storage
python -m src.dota_coach.cli fetch-matches-daily
```

## Troubleshooting

### Common Issues

**API Rate Limiting**:
- Use `--api-limit` to control daily usage
- Monitor with `status` command
- Rate limiting automatically applied

**Storage Space**:
- Configure external drive storage
- Monitor space with `status` command
- Raw matches are ~15KB each

**Data Quality**:
- Use `dashboard` to assess ML readiness
- Check `extract-topline` output for issues
- Validate with `status` command

### Getting Help

```bash
# Command-specific help
python -m src.dota_coach.cli COMMAND --help

# General help
python -m src.dota_coach.cli --help
```

---

*For detailed setup instructions, see [Getting Started Guide](getting-started.md)*