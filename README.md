# AI DotA Coach

AI-powered gaming coach that acts as your "pro friend sitting next to you" while playing Dota 2. Provides real-time strategic guidance through multi-modal interaction including voice and visual interfaces.

## 🎯 Vision

Build a comprehensive AI gaming companion that:
- **Learns from high-level gameplay** using ML models trained on parsed match data
- **Provides real-time strategic advice** during live games via GameState integration  
- **Communicates naturally** through voice and visual interfaces
- **Adapts to meta changes** with patch-aware recommendations

The goal: Enable strategic decision-making like a top-tier player without requiring deep meta-game knowledge or perfect mechanical skill.

> **[📋 Detailed Architecture](docs/architecture.md)** | **[🚀 Development Roadmap](docs/development-roadmap.md)**

## 🚀 About This Project

This is a personal learning journey exploring ML/AI product development, built entirely through AI-assisted coding. I enjoy Dota 2 but have a demanding job, and honestly, keeping up with the constantly evolving meta-game is exhausting. I wanted to build an AI companion that could help me make better strategic decisions in real-time, without spending hours analyzing patch notes and memorizing builds.  

Also, this is aligned with my personal goal to learn Machine Learning and AI, and I thought: why take a boring course when I can learn on the job? So here we are.

**What makes this interesting:**
- **AI-Assisted Development**: Built entirely using AI pair programming (Claude Code, Cursor, Codex) - every line of code, architecture decision, and documentation created through human-AI collaboration
- **Learning in Public**: Documenting the complete journey from initial concept to working product, including challenges, breakthroughs, and design decisions
- **Real-World Problem**: Solving an actual problem I face as a player - staying competitive without memorizing patch notes and meta shifts
- **Modern ML Pipeline**: Exploring practical implementation of ML models, real-time data processing, and multi-modal AI interfaces using current tools and techniques

**Why share this?** 
- Primarily to see if anyone out there on the internet would like to come along on this journey of building something challenging
- Provide a real-world case study of AI/ML product development

## 🚧 Current Status

**Phase 1: ML Model Foundation** (In Progress)
- ✅ **Operational Data Pipeline**: Match collection with state management and parse requests
- ✅ **Constants System**: Enhanced patch tracking with metadata and comprehensive logging  
- ✅ **CLI Framework**: Coaching interface with data collection and system management
- 🔴 **Current Blocker**: Hero filtering optimization (query timeouts prevent targeted data collection)
- ⏳ **Next Steps**: Data flattening, ML model training, enhanced coaching recommendations

## ⚡ Quick Start

### Prerequisites
- Python 3.12+
- OpenDota API key (for data collection)

### Installation

1. **Clone and setup:**
```bash
git clone <repository-url>
cd DotA_Coach
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your OpenDota API key
```

> **[📖 Detailed Setup Guide](docs/getting-started.md)**

### Basic Usage

```bash
# Get strategic coaching advice (placeholder logic)
python -m src.dota_coach.cli coach --hero vengeful_spirit --lane safe

# Check system status and data availability  
python -m src.dota_coach.cli status

# Update game constants from OpenDota
python -m src.dota_coach.cli update-constants

# Run daily match data collection
python -m src.dota_coach.cli fetch-matches-daily --api-limit 1800 --batch-size 50
```

## 🏗️ System Architecture

```
OpenDota Data → ML Models (Brain) → LLM Interface → Voice/Visual → User
                     ↑
               GameState API (Live Game Data)
```

**5-Phase Development:**
1. **ML Model Foundation** - Train strategic decision models on match data
2. **Real-Time Pipeline** - GameState API integration with ML models  
3. **LLM Interface Layer** - Natural language interpretation of ML outputs
4. **Voice Interface** - Speech-to-text input, text-to-speech output
5. **Visual Interface** - On-screen overlay for visual coaching prompts

## 🎮 MVP Hero Pool

Support heroes for initial model training:
- Vengeful Spirit | Witch Doctor | Lich
- Lion | Undying | Shadow Shaman

## 📁 Project Structure

```
DotA_Coach/
├── src/dota_coach/           # Core application
│   ├── match_pipeline.py     # Daily match collection with state management
│   ├── constants.py          # Enhanced patch tracking system
│   ├── cli.py               # Command-line interface
│   └── config.py            # Configuration management
├── data/                    # Data storage
│   ├── raw/matches/         # Raw match JSON files
│   ├── state/              # CSV state files for pipeline tracking
│   └── processed/          # ML-ready datasets (future)
├── constants/snapshots/     # Patch constants history
├── models/                 # Trained ML models (future)
├── docs/                   # Public documentation
└── personal_docs/          # Private development notes
```

> **[📂 Detailed Project Structure](docs/project-structure.md)**

## 🔧 Configuration

### Environment Variables (.env)
```bash
OPENDOTA_API_KEY=your_api_key_here
LOG_LEVEL=INFO
LOG_FILE=logs/dota_coach.log
DATA_DIR=data
CONSTANTS_DIR=constants  
MODELS_DIR=models
```

### Main Configuration (config.yaml)
- API settings and rate limits
- Data collection parameters  
- Hero pool configuration
- ML model parameters

## 🚀 Development Roadmap

### **Current Focus: Phase 1 - ML Model Foundation**
- 🔴 **Hero Filtering Optimization** (Critical Blocker)
- **Data Processing Pipeline** - Convert raw JSON to ML-ready datasets
- **Initial ML Model Training** - Item/skill/positioning recommendations  
- **Enhanced CLI Coach** - Replace placeholders with ML-powered advice

### **Upcoming Phases**
- **Phase 2**: Real-time GameState API integration
- **Phase 3**: LLM interface for natural language coaching
- **Phase 4**: Voice interface (STT/TTS)
- **Phase 5**: Visual overlay interface

> **[🗺️ Complete Development Roadmap](docs/development-roadmap.md)**

## 🤝 Contributing

This project follows systematic development principles:
- **Phase-gated progression** - No advancement until current phase complete
- **Outcome-focused tasks** - Each task represents 2-3 hours of focused work  
- **Quality standards** - Comprehensive testing and documentation
- **Architecture consistency** - Maintain separation between ML brain and interface layers

## 📚 Documentation

- **[🏗️ System Architecture](docs/architecture.md)** - Technical design and 5-phase vision
- **[📖 Getting Started](docs/getting-started.md)** - Detailed setup and usage guide
- **[🗺️ Development Roadmap](docs/development-roadmap.md)** - Current tasks and priorities
- **[📂 Project Structure](docs/project-structure.md)** - Codebase organization

## 💬 Support

For questions about setup, usage, or development:
1. Check the [Getting Started Guide](docs/getting-started.md)
2. Review the [Development Roadmap](docs/development-roadmap.md)  
3. Create an issue in the repository

---

*Building an AI-powered gaming companion that enhances strategic gameplay through intelligent, real-time decision support.*