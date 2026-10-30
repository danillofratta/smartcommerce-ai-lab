# SmartCommerce AI Lab

**Learn AI Engineering by building, testing, debugging, and comparing real patterns in one fictional commerce domain.**

> **Status:** Planning / documentation scaffold. The modules and CLI below describe the intended roadmap; no runnable lab is included in this initial documentation bundle.

## Why this project?

Instead of collecting disconnected LLM demos, this repository will use the **same fictional e-commerce environment**—customers, orders, payments, inventory, shipping, support, and refunds—to explore AI engineering techniques.

The goal is to understand **when a technique is appropriate, how to implement it, how it fails, and how to prove that it works**. More agents are not automatically better.

### Core topics

| Area | Examples |
|---|---|
| Agent orchestration | Sequential, router, ReAct, parallel, evaluator–optimizer, supervisor, HITL, planner, hierarchical teams |
| RAG engineering | Naive, hybrid, reranking, multi-query, parent-document, metadata filtering, agentic, corrective, self-RAG, Graph RAG |
| AI evaluations | Golden datasets, deterministic evaluators, LLM-as-a-judge, RAG metrics, agent trajectory, regression tests, experiments |
| Tools and MCP | Function calling, typed contracts, MCP servers/clients, authorization, retries |
| Memory and context | Checkpoints, summarization, long-term memory, selective retrieval, context budgets |
| Security | Guardrails, prompt injection, PII handling, tool authorization, tenant isolation, adversarial tests |
| Prompts and generation | Structured outputs, prompt versioning, comparison, validation |
| LLMOps | Tracing, cost, latency, evaluation on traces, release gates |
| Data and knowledge | Ingestion, chunking, indexing, freshness, metadata access controls |
| Model engineering | Provider selection, fallbacks, caching, rate limits, cost/quality trade-offs |
| Reliability | Durable execution, idempotency, retries, bounded loops, recovery |
| Agent skills | Reusable skill definitions, discovery, progressive loading, skill security |
| Multimodal | Invoice extraction, product-damage analysis, document understanding |
| Analytics | Read-only Text-to-SQL, schema retrieval, SQL validation |
| Production engineering | APIs, async streaming, CI, deployment, observability, secrets |
| Advanced / research | Planning systems, model adaptation, fine-tuning, distillation, UX and governance |

## One domain, comparable problems

Example requests will include:

- “Where is order 1024, and has it been paid?”
- “I purchased a laptop 18 days ago. Can I return it?”
- “I was charged twice and my delivery is late.”
- “Please issue a refund of R$ 2,500.” (simulated with human approval)
- “Which orders were delivered late this week?”

All commerce data is **synthetic**. No real payments or refunds are processed.

## Planned repository layout

```text
labs/
  00_foundations/
  01_orchestration/
  02_rag/
  03_evaluations/
  04_tools_mcp/
  05_memory_context/
  06_guardrails_security/
  07_prompt_structured/
  08_observability_llmops/
  09_data_knowledge/
  10_model_cost/
  11_reliability/
  12_agent_skills/
  13_multimodal/
  14_analytics_sql/
  15_platform_delivery/
  16_advanced_agents/
  17_model_adaptation/
  18_ai_product_governance/
smartcommerce/   # synthetic fixtures, policy documents and safe local tools
benchmarks/      # shared datasets, evaluators and measured reports
tests/
docs/
```

Only implemented modules will be added to the repository over time.

## Planned CLI (not yet implemented)

```bash
python lab.py list
python lab.py run orchestration/router --mode mock --case ROUTE-001
python lab.py run orchestration/router --mode live --case ROUTE-001
python lab.py graph orchestration/router
python lab.py eval rag --dataset refunds_v1 --mode live
```

Every lab should have a small, understandable entry point, an architecture diagram, deterministic test cases, clear logs and a README explaining its state transitions and trade-offs.

## Learning principles

1. **Understand first:** draw the flow and define state/contracts before coding.
2. **Compare fairly:** reuse fixtures and datasets when comparing strategies.
3. **Mock ≠ measurement:** mocked flows teach mechanics; live runs provide empirical evidence.
4. **Test behavior:** validate normal, failure, limit and adversarial cases.
5. **Measure quality:** use task-appropriate evaluations rather than relying on “looks good”.
6. **Secure actions:** allow LLMs to reason or propose; enforce permissions and business invariants in deterministic code.
7. **Make it explainable:** each lab includes a debugging exercise and a manual modification challenge.

## Stack direction

Python, LangGraph, Pydantic, Groq/ChatGroq, pytest and optional Langfuse. Additional technologies (MCP SDK, vector databases, Ragas, FastAPI, Docker, OpenTelemetry, etc.) will be introduced only when a lab benefits from them. Versions will be pinned and validated during implementation.

## Project documents

- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) — canonical goals, constraints, architecture, competencies and hand-off instructions.
- [LEARNING_PATH.md](LEARNING_PATH.md) — prioritized study roadmap.
- [LAB_TEMPLATE.md](LAB_TEMPLATE.md) — required structure and evidence for a lab.

## License and roadmap

A license will be selected before public release. **Documentation scaffold only** in the initial version; don't treat planned features as implemented.
