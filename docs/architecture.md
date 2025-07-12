# System Architecture

## Overview

DotA Coach is designed as a comprehensive AI gaming companion built on a 5-phase architecture that progresses from foundational ML capabilities to sophisticated multi-modal interaction.

## Core Vision

```
"AI Pro Friend" - A sophisticated gaming companion that provides real-time strategic guidance
through natural voice and visual interfaces, powered by ML models trained on high-level gameplay.
```

## System Components

### 1. ML Model (The Brain)
- **Purpose**: Learn optimal strategic decisions from parsed match data
- **Input**: Game state information (items, levels, positions, cooldowns)
- **Output**: Structured recommendations (item purchases, skill upgrades, positioning)
- **Training Data**: OpenDota parsed matches from high-MMR games

### 2. GameState Integration
- **Purpose**: Real-time awareness of current game situation
- **Technology**: Valve's Game State Integration (GSI) API
- **Data Flow**: Live game state → ML model input format
- **Update Frequency**: ~200ms real-time updates

### 3. LLM Interface Layer
- **Purpose**: Translate ML outputs into natural language advice
- **Input**: Structured ML recommendations + game context
- **Output**: Natural language coaching advice
- **Reasoning**: ML models output structured data, LLMs provide natural communication

### 4. Voice Interface
- **Speech-to-Text**: Capture user questions during gameplay
- **Text-to-Speech**: Deliver strategic advice via voice
- **Design Goal**: Hands-free interaction without disrupting gameplay

### 5. Visual Interface
- **Overlay System**: On-screen display for visual prompts
- **Information Hierarchy**: Strategic recommendations, timing alerts, contextual data
- **Integration**: Coordinated with voice interface for multi-modal experience

## Data Flow Pipeline

### Training Phase (Current - Phase 1)
```
OpenDota API → Raw Match JSON → Data Flattening → ML Training → Trained Models
```

### Real-Time Operation (Future - Phase 2+)
```
GameState API → ML Model → Structured Output → LLM Layer → Voice/Visual → User
```

## 5-Phase Development Architecture

### Phase 1: ML Model Foundation
**Goal**: Train strategic decision models using OpenDota match data
- Data collection pipeline with state management
- Match data flattening and feature engineering
- ML model training for item/skill/positioning decisions
- **Current Status**: Data pipeline operational, hero filtering optimization needed

### Phase 2: Real-Time Pipeline
**Goal**: Integrate GameState API with trained ML models
- Valve GSI integration for live game data
- Real-time inference pipeline (<200ms ML processing)
- Structured output format for LLM consumption

### Phase 3: LLM Interface Layer
**Goal**: Natural language interpretation of ML recommendations
- ML output schema design for LLM understanding
- Dota 2 knowledge base for contextual advice
- Prompt engineering for consistent, natural coaching

### Phase 4: Voice Interface
**Goal**: Hands-free interaction through speech
- Speech-to-text for user questions/commands
- Text-to-speech for AI response delivery
- Conversation flow design for gaming environment

### Phase 5: Visual Interface
**Goal**: On-screen overlay for visual coaching prompts
- Game overlay framework research and implementation
- Visual information hierarchy design
- Multi-modal integration with voice interface

## Technical Specifications

### Performance Requirements
- **ML Inference**: <200ms for strategic recommendations
- **LLM Processing**: <1.5 seconds for natural language generation
- **Total Response Time**: <2.5 seconds from game state change to user advice
- **Voice Latency**: <800ms for speech synthesis

### Data Requirements
- **Training Data**: 1000+ matches per MVP hero (6 support heroes)
- **Match Quality**: High-MMR games (top 1-2%) for optimal decision patterns
- **Patch Currency**: Current patch data only for model training
- **Storage**: ~250-400MB monthly for match data collection

### Scalability Design
- **Modular Architecture**: Independent development of ML brain vs interface layers
- **API Integration**: Standardized interfaces between components
- **Future-Proof**: Extensible to additional heroes, game modes, advanced ML architectures

## Training Data Strategy

### OpenDota Parsed Matches
- **Rich Strategic Information**: Teamfight breakdowns, item usage, economic tracking
- **Decision Context**: Strategic timing decisions and their outcomes
- **Temporal Analysis**: Match timeline data for decision sequences
- **Quality Focus**: High-MMR matches for optimal strategic patterns

### Feature Engineering
- **Strategic Decision Points**: Item purchases, skill upgrades, positioning choices
- **Game State Context**: Economic state, team composition, match timing
- **Outcome Correlation**: Decision impact on match progression and results

## Success Metrics

### Phase 1 Completion
- Hero filtering optimization resolved (>1000 matches per hero collected)
- ML models trained with >70% accuracy vs high-MMR player decisions
- Enhanced CLI providing data-driven strategic recommendations

### Overall System Success
- Measurable improvement in user strategic decision-making
- <2 second response time for real-time advice
- Natural, contextually appropriate coaching in Dota 2 terminology
- Hands-free operation without disrupting gameplay

## Future Enhancements

### Advanced ML Capabilities
- Transformer architectures for sequence modeling
- Reinforcement learning for adaptive strategies
- Multi-hero team coordination modeling

### Extended Functionality
- Draft phase analysis and hero selection advice
- Advanced macro strategy (objective timing, map control)
- Integration with streaming/content creation tools
- Mobile companion app for pre-game preparation

---

*This architecture enables systematic progression from foundational ML capabilities to a sophisticated, multi-modal AI gaming companion that enhances strategic gameplay through intelligent real-time decision support.*