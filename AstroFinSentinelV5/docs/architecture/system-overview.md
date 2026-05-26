# AstroFinSentinelV5 — System Architecture

**ATOM-META-RL-024 | Last Updated: 2026-05-26**

---

# 1. Layered Architecture

AstroFinSentinelV5 follows a layered autonomous multi-agent architecture designed around probabilistic orchestration, adaptive meta-learning, and risk-constrained execution.

The system is organized into seven primary layers:

```text
┌──────────────────────────────────────────────────────────────┐
│ PRESENTATION LAYER                                          │
│ CLI / Future REST / Dashboards                              │
├──────────────────────────────────────────────────────────────┤
│ ORCHESTRATION LAYER                                         │
│ Routing / Thompson Sampling / Parallel Coordination         │
├──────────────────────────────────────────────────────────────┤
│ AGENT LAYER                                                 │
│ Specialist Agents / Councils / Synthesis                    │
├──────────────────────────────────────────────────────────────┤
│ CORE SERVICES LAYER                                         │
│ Ephemeris / Beliefs / Rewards / Coordination                │
├──────────────────────────────────────────────────────────────┤
│ META-LEARNING LAYER                                         │
│ Evolution / OAP / KARL / Strategy Optimization              │
├──────────────────────────────────────────────────────────────┤
│ TRADING LAYER                                               │
│ Risk Engine / Broker Adapters / Execution                   │
├──────────────────────────────────────────────────────────────┤
│ DATA LAYER                                                  │
│ PostgreSQL / SQLite / FAISS / Session Persistence           │
└──────────────────────────────────────────────────────────────┘
2. Subsystem Responsibilities
Presentation Layer
Purpose

Responsible for operator interaction, CLI execution, monitoring access, and future API exposure.

Components
orchestration/karl_cli.py
dashboard integrations
future REST API adapters
Responsibilities
user command intake
CLI workflow management
operational visibility
external API integration
Orchestration Layer
Purpose

Coordinates execution flow between agents, routing logic, probabilistic selection, and synthesis pipelines.

Components
orchestration/sentinel_v5.py
orchestration/sentinel_v5_mas.py
LangGraph execution graph
Thompson selection pipeline
Responsibilities
query routing
shared-state propagation
parallel execution
topology coordination
orchestration lifecycle management
Core Patterns
Thompson sampling
asynchronous fan-out execution
stateful orchestration graphs
topology-driven execution
Agent Layer
Purpose

Produces specialized signals and domain intelligence.

Components
agents/
agents/_impl/
Agent Categories
technical analysis agents
macroeconomic agents
astrology agents
electoral cycle agents
sentiment agents
synthesis coordinators
AMRE-enhanced reflective agents
Responsibilities
signal generation
confidence estimation
domain analysis
synthesis participation
self-calibration
Core Services Layer
Purpose

Provides deterministic shared infrastructure and mathematical utilities.

Components
core/ephemeris.py
core/thompson.py
core/reward_engine.py
core/council/
core/coordination/
Responsibilities
ephemeris calculations
Bayesian belief tracking
reward computation
council aggregation
pressure field coordination
statistical selection logic
Meta-Learning Layer
Purpose

Implements adaptive optimization and long-horizon learning.

Components
meta_rl/meta_agent.py
meta_rl/oap/
meta_rl/quant/
meta_rl/distributed/
meta_rl/lineage/
Responsibilities
strategy evolution
OAP optimization
genetic operations
strategy persistence
regime adaptation
drift analysis
KARL memory management
Trading Layer
Purpose

Handles safe trade execution and exposure management.

Components
trading/risk_engine_v2.py
trading/safety_gate.py
trading/broker.py
execution algorithms
Responsibilities
risk validation
broker communication
exposure checks
correlation management
TWAP/VWAP execution
mode enforcement
Data Layer
Purpose

Provides persistence, retrieval, vector search, and historical storage.

Components
db/
knowledge/
PostgreSQL repositories
SQLite state storage
FAISS vector indexes
Responsibilities
persistent storage
vector retrieval
belief persistence
session archiving
historical trade storage
RAG indexing
3. Component Boundaries

The architecture separates deterministic infrastructure from adaptive intelligence components.

Orchestration ↔ Agents
Contract
AgentState
AgentResponse
Rules
orchestration coordinates only
agents generate signals
orchestration does not compute market intelligence directly
Agents ↔ Core Services
Contract

Shared deterministic utility access.

Rules
agents consume beliefs/rewards
agents do not directly mutate persistence
shared infrastructure remains deterministic
Meta-RL ↔ Trading
Contract

Optimization feedback only.

Rules
Meta-RL proposes adjustments
trading layer enforces hard safety constraints
execution authority remains in RiskEngineV2
Trading ↔ Broker
Contract

Broker adapter abstraction layer.

Rules
all orders pass through SafetyGate
broker-specific logic isolated
execution algorithms remain reusable
Knowledge ↔ Agents
Contract

Retrieval-only interaction.

Current State

Partially implemented.

knowledge/rag_retriever.py exists but is not fully integrated into agent prompts.

4. Orchestration Topology

AstroFinSentinelV5 supports two orchestration models.

Standard Execution Path
User Query
    ↓
Router
    ↓
ThompsonSampler
    ↓
Parallel Agent Execution
    ↓
SynthesisAgent
    ↓
RiskEngineV2
    ↓
Broker Execution
Characteristics
deterministic topology
lower orchestration overhead
production-oriented execution
direct coordination flow
MAS Factory Execution Path
User Query
    ↓
MASFactoryArchitect
    ↓
Topology Generation
    ↓
TopologyExecutor
    ↓
Dynamic Agent Graph
    ↓
Synthesis
    ↓
Risk Validation
    ↓
Execution
Characteristics
dynamic topology construction
adaptive graph execution
topology mutation support
experimental orchestration flexibility
5. Architectural Principles

The platform is designed around the following principles:

probabilistic coordination
modular specialization
adaptive reinforcement learning
bounded persistent state
asynchronous parallel execution
explainable synthesis
strict risk isolation
deterministic execution gates
6. Current Architectural Constraints

Known limitations include:

RAG subsystem not fully integrated
synchronous SQLite in async execution paths
single broker dependency
duplicated type definitions
fragmented persistence implementations
feature flag proliferation

These issues are tracked in:

docs/architecture/technical-debt.md
docs/architecture/risk-register.md
7. Future Evolution Direction

Planned architectural evolution includes:

distributed orchestration
multi-broker execution support
Redis-backed orchestration state
topology mutation at runtime
stateless orchestration scaling
unified feature configuration
production observability stack
resilient RAG integration
