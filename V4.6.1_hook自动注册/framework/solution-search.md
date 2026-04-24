# SuperTeam Stage-2 Solution Search Contract

This document defines how `SuperTeam` should search outward during `design` for brand-new projects and internal products.

## Core Principle

Stage-2 search is **problem search**, not **project-name search**.

- do **not** start by searching the new product's name
- do **not** assume the target project already has an official site, official GitHub repo, or existing community discussion
- start from the clarified problem, extract anchors, and search for mature solution patterns around those anchors

## Search Inputs

Use `.superteam/runs/<task-slug>/project-definition.md` as the source of truth.

Before outward search, extract five anchor types when relevant:

- `function anchors` — core capabilities the project must provide
- `workflow anchors` — real business flows the system must support
- `role anchors` — actors, approval roles, and operational responsibilities
- `constraint anchors` — technical, operational, compliance, or platform boundaries
- `decision anchors` — the specific stage-2 questions that must be decided before planning

If the stage cannot name the anchors, it is not ready for meaningful outward search.

## Default Search Order

For brand-new products, use this order unless a clear reason exists to skip a layer:

1. `market-patterns` — keyword web search (`Google` or an equivalent search engine) for mature products, solution pages, comparisons, and workflows
2. `mature-implementations` — GitHub keyword search for open-source implementations, examples, repo structures, and module boundaries
3. `official-constraints` — official docs for frameworks, platforms, APIs, regulations, and integration boundaries that the new project depends on
4. `community-signals` — community posts, blog posts, issues, discussions, or operator writeups that expose real-world adoption and maintenance signals
5. `failure-signals` — postmortems, migration stories, negative reviews, anti-pattern writeups, issue clusters, or "why we moved away from X" material

This order intentionally treats `official` as a **constraint-validation layer**, not the default starting point for a brand-new internal product.

## Search Layers

### 1. `market-patterns`

Goal:

- discover what mature market solutions usually look like
- identify standard module cuts, workflows, and business expectations

Typical sources:

- search-engine results
- product pages
- industry solution pages
- comparison pages
- case-study pages

### 2. `mature-implementations`

Goal:

- discover how related systems are actually implemented
- inspect repo structure, permission models, data boundaries, and module design

Typical sources:

- GitHub repositories
- GitHub topics
- examples and starters
- README files
- discussions and issue trackers

### 3. `official-constraints`

Goal:

- validate what the chosen direction can or cannot do because of external dependencies

Typical sources:

- framework docs
- API docs
- platform docs
- compliance docs
- hosting / deployment / browser / app-store constraints

### 4. `community-signals`

Goal:

- collect operator reality, adoption signals, implementation pain, and scaling feedback

Typical sources:

- Reddit
- Hacker News
- Zhihu
- Juejin
- blogs
- issue discussions

### 5. `failure-signals`

Goal:

- learn what should not be copied blindly
- identify where mature-looking patterns fail in practice

Typical sources:

- postmortems
- migration stories
- negative reviews
- issue clusters
- anti-pattern articles

## Keyword Generation Rule

Search keywords should be generated from anchors, not improvised from the project title alone.

For each important anchor, generate search terms in combinations such as:

- `function phrase`
- `workflow phrase`
- `role + workflow`
- `constraint + capability`
- `English equivalent`
- `anti-pattern / failure phrase`

Examples:

- `门店考勤管理系统`
- `门店日报 审核 流程`
- `store attendance dashboard`
- `multi branch reporting permission model`
- `attendance system adoption problems`

## Breadth Pass vs Validation Pass

Stage-2 search should normally run in two passes.

### Pass A — Breadth

Purpose:

- discover the option landscape quickly
- avoid solving the problem from one reference or one gut feeling

Default breadth actions:

- web keyword search for market patterns
- GitHub keyword search for mature implementations
- create initial evidence cards grouped by anchor

### Pass B — Validation

Purpose:

- test the most promising directions against constraints and risks

Default validation actions:

- inspect official dependency constraints
- inspect community implementation feedback
- inspect failure signals and anti-patterns
- record whether each strong option is supported, weakened, or contradicted

## `solution-landscape.md` Search Framing Minimums

The search framing section should state:

- anchor list
- keyword matrix or representative keyword groups
- search layers covered
- search layers skipped with reason
- breadth-pass summary
- validation-pass summary
- unresolved contradictions

## Evidence Card Additions

Every evidence card should contain at least:

- `source`
- `source type`
- `search layer`
- `matched anchors`
- `problem it solves`
- `solution pattern`
- `supports or challenges which option`
- `what is worth borrowing`
- `what should not be copied blindly`
- `applicability conditions`
- `risks or caveats`

## Search Completion Test

Stage-2 search is good enough to support a decision when:

- the major decision anchors are covered
- at least one breadth pass and one validation pass happened for meaningful work
- both `market-patterns` and `mature-implementations` were attempted unless clearly irrelevant
- critical dependency constraints are checked when they exist
- at least one failure-signal sweep happened for non-trivial work
- the evidence package can clearly explain both `borrow` and `do-not-copy` choices

## Anti-Patterns

- searching the project name instead of the clarified problem
- treating `official docs first` as a universal rule for brand-new products
- copying a product page without checking how it is actually implemented
- copying an open-source repo without checking market expectations or failure signals
- stopping after one fast search pass
- collecting links without mapping them back to anchors and candidate options

## Example Framing

If the project is a new `门店信息管理系统`, search should not begin with that exact product name.

It should begin with anchors such as:

- `门店考勤`
- `门店日报`
- `门店月报`
- `巡店记录`
- `多门店权限`

Then search outward for:

- mature store operations products
- GitHub implementations for attendance/reporting/inspection/permission models
- official docs for the chosen external dependencies
- community complaints and scaling issues
- failure signals around adoption, reporting accuracy, and permission complexity
