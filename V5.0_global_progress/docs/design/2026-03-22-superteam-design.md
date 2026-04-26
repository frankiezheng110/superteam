# SuperTeam Design

Date: 2026-03-22
Location: `D:\opencode项目\superteam`

## 1. Project Definition

SuperTeam is an orchestration framework for multi-agent software delivery centered on explicit stage-to-teammate interface contracts.

Its core idea is:

- let `Superpowers` own the stage methodology;
- let source-derived teammate collaboration rules shape worker behavior;
- build a local orchestration framework that keeps both sides coherent through explicit contracts.

This is not a direct merge of two repositories. It is a new project that studies both, extracts stable rules, and reassembles them into a maintainable local framework.

## 2. Goals

The first version should achieve these goals:

1. define a stable project architecture for stage-based multi-agent work;
2. document the contract between stage rules and teammate behaviors;
3. create a local workspace structure for research, framework assets, and adapted agents;
4. prepare a roadmap that can move from design into rule extraction and implementation.

## 3. Non-Goals

The first version does not attempt to:

- fully reimplement either upstream project;
- ship automation scripts before rule boundaries are clear;
- solve every prompt conflict up front;
- optimize for benchmark comparison with Claude Code.

Comparison may be used later for review, but it is not the primary design driver.

## 4. Design Principles

### 4.1 One primary owner per concern

- Stage sequencing, completion gates, and methodology come from `Superpowers`.
- Team coordination and role boundaries come from extracted teammate patterns rather than a direct upstream copy.
- When two rules overlap, each rule must have a single owner instead of hybrid wording.

### 4.1.1 Responsibility map

| Concern | Primary layer |
| --- | --- |
| Stage sequencing | Method Layer |
| Completion gates | Method Layer |
| Teammate role boundaries | Team Layer |
| Handoff artifact format | Interface Layer |
| Review contract | Interface Layer |
| Escalation path | Interface Layer |

### 4.2 Context should be externalized

Persistent work should rely on handoff artifacts, plans, and review outputs instead of hidden conversational memory.

### 4.3 Start with a rule compatibility layer

The first implementation target is documentation plus structured definitions, not automation. This lowers integration risk and makes later scripting safer.

### 4.4 Minimal but extensible structure

Only create directories and files that immediately support design, planning, and research. Avoid speculative scaffolding.

## 5. Architecture Overview

SuperTeam has three layers.

### 5.1 Method Layer

This layer defines the global workflow:

1. clarify intent;
2. design the solution;
3. write plan;
4. execute;
5. review;
6. verify;
7. finish and hand off.

Its job is to answer: what stage are we in, what must happen before moving on, and what evidence is required.

### 5.2 Team Layer

This layer defines teammate-style responsibilities:

- planner
- architect
- critic
- executor
- verifier
- supporting specialist roles added later

Its job is to answer: who owns which activity, what they may or may not do, and what artifact they must produce.

### 5.3 Interface Layer

This layer connects stages to teammates through explicit contracts:

- input artifact
- expected output artifact
- completion criteria
- escalation path

This interface layer is the integration core of SuperTeam. It prevents the project from becoming a loose mix of two upstream philosophies.

## 6. Initial Repository Structure

### `README.md`

Project identity, scope, and current status.

### `docs/design/`

Design specs that define the architecture before implementation.

### `docs/research/`

Source extraction notes for the two upstream inputs, including rule inventories and conflict findings.

### `framework/`

Core orchestration artifacts such as:

- stage model
- handoff templates
- execution constraints
- review contracts

In the initial delivery round, this directory was intended as skeleton first. In the delivered v1 docs-first state, it contains real framework documents.

### `agents/`

Adapted teammate role definitions for the local framework.

In the initial delivery round, this directory was intended as skeleton first. In the delivered v1 docs-first state, it contains real agent definitions.

### `skills/`

User-facing stage entry points and higher-level workflow wrappers.

In the initial delivery round, this directory was intended as skeleton first. In the delivered v1 docs-first state, it contains real skill documents.

### `plan/`

Execution roadmaps derived from the approved design.

## 7. First Delivery Scope

The initial delivery round was scoped to produce:

1. this design spec;
2. the repository skeleton;
3. a phase-based project plan.

This section records the original initialization scope. The current repository has progressed beyond placeholder structure into a docs-first v1 framework deliverable.

## 8. Planned Implementation Sequence

### Phase A: Design

Lock the project definition, boundaries, and architecture.

### Phase B: Research Extraction

Collect and organize source rules from the upstream inputs into local research docs.

### Phase C: Conflict Mapping

Identify overlapping or incompatible rules and assign a primary owner for each concern.

### Phase D: Framework Definition

Write the local stage contracts, handoff formats, and review rules.

### Phase E: Agent and Skill Adaptation

Create adapted teammate definitions and stage entry skills.

### Phase F: Validation

Run the framework against a real task and record observations.

## 9. Review Focus

The design should be reviewed against four questions:

1. Is the project clearly a new framework instead of a direct copy?
2. Are stage rules and teammate rules separated cleanly?
3. Does the directory structure match the architecture?
4. Is the first delivery scope small enough to execute safely?

## 10. Current Decision

Proceed with a design-first independent version of SuperTeam in the current workspace.
