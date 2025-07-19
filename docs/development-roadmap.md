# Development Roadmap

## Current Status: Phase 1 - ML Model Foundation

**Goal**: Train ML models on OpenDota match data for strategic decision making

### 🎯 Project Overview
Building an AI-powered Dota 2 gaming companion through 5 systematic phases:
- **Phase 1**: ML Model Foundation (Current Focus)
- **Phase 2**: Real-Time Pipeline (GameState → ML)
- **Phase 3**: LLM Interface Layer
- **Phase 4**: Voice Interface
- **Phase 5**: Visual Interface

---

## ✅ COMPLETED - Foundation Setup

### Infrastructure & Systems
- ✅ **Complete Project Structure**: Python modules, testing framework, configuration management
- ✅ **Enhanced Constants System**: Patch tracking with metadata, comprehensive logging, change detection
- ✅ **Operational Match Pipeline**: Daily collection with CSV state management, parse requests, deduplication
- ✅ **CLI Framework**: Status monitoring, data collection, coaching interface with tested commands

### Technical Achievements
- **Robust State Management**: CSV-based tracking prevents data loss across pipeline runs
- **API Integration**: Working patterns established for OpenDota endpoints
- **Configuration System**: Centralized management for all system components
- **Error Handling**: Graceful handling of API failures, timeouts, and edge cases

---

## 🚧 PHASE 1: ML Model Foundation (In Progress)

**Current Focus**: ML model training using structured data insights from dashboard analysis

### ✅ RESOLVED - Hero Filtering Implementation
**Solution**: Implemented working hero filtering using array concatenation SQL pattern
**Achievement**: 5x API efficiency improvement for targeted support hero collection
**Status**: Operational filtering for 7 MVP support heroes with no timeout issues

### ✅ COMPLETED - Data Analysis Dashboard
**Implementation**: CSV extraction and per-hero ML readiness assessment system
**Features**: 
- Comprehensive rank cleaning and data validation
- Per-hero ML training assessment with unique player metrics
- Dashboard generation with actionable recommendations
**Impact**: Clear foundation for ML model development with quality insights

### 🎯 CURRENT PRIORITIES - ML Model Training
**Outcome**: Train ML models using dashboard insights for strategic decision making
**Estimated Effort**: 4-6 work sessions (12-18 hours)

**Tasks:**
- Build comprehensive data flattening system for parsed match JSON structure
- Extract strategic decision points: item purchases, skill upgrades, positioning choices
- Create temporal feature engineering for decision timing and game state context
- **Success Criteria**: Structured datasets ready for ML training with rich strategic features

### 🧠 Initial ML Model Training
**Outcome**: Train and validate first strategic decision models  
**Estimated Effort**: 3-4 work sessions (9-12 hours)

**Tasks:**
- Develop item purchase recommendation model using match timeline data
- Create skill upgrade timing model based on game state patterns
- Build positioning/playstyle classification (aggressive/defensive/farming)
- **Success Criteria**: >70% accuracy on held-out test data compared to high-MMR player decisions

### 🎮 Enhanced CLI Coach
**Outcome**: Replace placeholder logic with actual ML-powered recommendations
**Estimated Effort**: 2-3 work sessions (6-9 hours)

**Tasks:**
- Integrate trained models into CLI coaching interface
- Implement real-time inference pipeline for coaching recommendations  
- Add model confidence scores and alternative suggestion system
- **Success Criteria**: CLI provides data-driven strategic advice based on trained models

### Phase 1 Gate Requirements
**No progression to Phase 2 until all Phase 1 tasks complete:**
- ✅ Hero filtering optimization resolved
- ✅ Data processing pipeline operational
- ✅ ML models trained and validated
- ✅ Enhanced CLI coach implemented

---

## 🔄 PHASE 2: Real-Time Pipeline (Future)

**Goal**: Integrate GameState API with trained ML models for live game coaching
**Prerequisites**: Phase 1 complete with trained ML models

### GameState API Integration
**Outcome**: Capture and process live game data from Valve's Game State Integration
**Estimated Effort**: 3-4 work sessions (9-12 hours)

**Tasks:**
- Set up GSI listener for real-time Dota 2 game state capture
- Map GSI JSON format to ML model input requirements
- Build data transformation pipeline for live inference
- **Success Criteria**: Real-time game state data flowing into ML models during live games

### Real-Time Inference Pipeline  
**Outcome**: ML models provide strategic recommendations during active gameplay
**Estimated Effort**: 2-3 work sessions (6-9 hours)

**Tasks:**
- Optimize ML models for low-latency inference (<200ms response time)
- Create structured output format for downstream LLM consumption
- Implement error handling and fallback logic for game state edge cases
- **Success Criteria**: <2 second total response time from game state change to recommendation

### Live Testing & Validation
**Outcome**: Validate system performance during actual Dota 2 matches
**Estimated Effort**: 2-3 work sessions (6-9 hours)

**Tasks:**
- Test pipeline stability during full game sessions
- Measure recommendation accuracy against post-game analysis
- Optimize performance for consistent real-time operation
- **Success Criteria**: Stable operation through complete matches with relevant strategic advice

---

## 🤖 PHASE 3: LLM Interface Layer (Future)

**Goal**: Natural language interpretation of ML model outputs
**Prerequisites**: Phase 2 complete with operational real-time pipeline

### ML Output Schema Design
**Outcome**: Structured format that LLMs can interpret and verbalize effectively
**Estimated Effort**: 2-3 work sessions (6-9 hours)

**Tasks:**
- Design ML model output schema with reasoning codes and confidence scores
- Create comprehensive Dota 2 knowledge base for LLM context
- Build prompt engineering system for consistent advice generation
- **Success Criteria**: LLM produces natural, contextually appropriate coaching advice

### LLM Integration & Testing
**Outcome**: Seamless translation from ML recommendations to natural language
**Estimated Effort**: 3-4 work sessions (9-12 hours)

**Tasks:**
- Implement LLM API integration with optimized prompts
- Test interpretation quality across diverse game scenarios
- Build conversation flow for reactive Q&A during gameplay
- **Success Criteria**: Natural language advice that accurately reflects ML model insights

---

## 🎤 PHASE 4: Voice Interface (Future)

**Goal**: Hands-free interaction through speech recognition and synthesis
**Prerequisites**: Phase 3 complete with operational LLM interface

### Speech-to-Text Integration
**Outcome**: Reliable voice command recognition during gameplay
**Estimated Effort**: 2-3 work sessions (6-9 hours)

**Tasks:**
- Integrate STT API for user question/command capture
- Design command patterns and conversation flows
- Optimize for gaming environment noise and quick interactions
- **Success Criteria**: Accurate voice command recognition without disrupting gameplay

### Text-to-Speech Implementation
**Outcome**: Natural voice delivery of strategic advice
**Estimated Effort**: 2-3 work sessions (6-9 hours)

**Tasks:**
- Implement TTS API for AI response delivery
- Optimize voice synthesis for quick, clear communication
- Test audio quality and timing during active gameplay
- **Success Criteria**: Clear, timely voice advice that enhances rather than distracts from gameplay

---

## 📺 PHASE 5: Visual Interface (Future)

**Goal**: On-screen overlay for visual coaching prompts and information display
**Prerequisites**: Phase 4 complete with operational voice interface

### Overlay Framework Research & Design
**Outcome**: Technical foundation for game overlay system
**Estimated Effort**: 3-4 work sessions (9-12 hours)

**Tasks:**
- Research game overlay frameworks and implementation approaches
- Design visual information hierarchy and layout principles
- Create mockups for different types of strategic information display
- **Success Criteria**: Clear technical path and design specifications for overlay implementation

### Visual Interface Implementation
**Outcome**: Production-ready overlay system integrated with voice interface  
**Estimated Effort**: 4-5 work sessions (12-15 hours)

**Tasks:**
- Implement overlay rendering system with game integration
- Create visual representations for different recommendation types
- Integrate with voice interface for cohesive multi-modal experience
- **Success Criteria**: Functional overlay that enhances strategic decision-making without cluttering game view

---

## 📋 Development Principles

### Task Organization
- **Outcome-Focused**: Each task targets specific deliverable with clear success criteria
- **Time-Boxed**: Tasks represent 2-3 hours of focused work per session
- **Phase-Gated**: No advancement until previous phase 100% complete
- **Quality-First**: Comprehensive testing and documentation required

### Technical Standards
- **Modular Architecture**: Maintain separation between ML brain and interface layers
- **Performance Benchmarks**: Establish and maintain response time requirements
- **Error Handling**: Graceful degradation for all system components
- **Scalability**: Design for future enhancement and additional heroes

### Current Priorities (Phase 1)
1. **Hero Filtering Research**: Critical blocker for targeted data collection
2. **Data Pipeline Completion**: Enable ML model training
3. **ML Model Development**: Foundation for strategic recommendations
4. **CLI Enhancement**: Operational coaching interface

## 🎯 Success Metrics

### Phase 1 Completion
- **Data Collection**: 1000+ matches per MVP support hero
- **ML Accuracy**: >70% agreement with high-MMR player decisions
- **CLI Functionality**: Data-driven recommendations replace placeholder logic
- **System Stability**: Consistent operation across all components

### Overall Project Success
- **Response Time**: <2.5 seconds from game state change to user advice
- **Recommendation Quality**: Natural, contextually appropriate strategic advice
- **User Experience**: Measurable improvement in strategic decision-making
- **Multi-Modal Operation**: Seamless voice and visual interface integration

---

*This roadmap guides systematic development from foundational ML capabilities through sophisticated multi-modal interaction, ensuring each phase builds reliably on the previous foundation.*