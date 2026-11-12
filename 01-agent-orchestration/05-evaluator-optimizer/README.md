# Evaluator–Optimizer

Generate a customer support response, audit it, and revise it using feedback.
Python decides refund eligibility using fictional policies. The LLM drafts and
reviews wording; it cannot execute refunds or override eligibility.

```mermaid
flowchart LR
    START --> Policy
    Policy --> Generator
    Generator --> Evaluator
    Evaluator -->|Approved| Finalizer
    Evaluator -->|Rejected, fewer than 3 attempts| Generator
    Evaluator -->|Rejected, 3 attempts| Finalizer
    Finalizer --> END
```

The shared `RefundState` holds the request, order, policy result, draft, feedback,
attempt counter, guardrail issues, evaluation verdict, final status, and final
response. Each revision receives the previous draft and feedback, including
missing requirements and deterministic validation issues. The policy node runs
once per invocation; the finalizer recalculates the policy to check consistency.

The evaluator approves only when its structured verdict is positive, its list
of missing requirements is empty, and `validate_draft` reports no issues. After
approval or exhaustion, the finalizer rechecks policy consistency and the draft.
It publishes a fixed policy-specific message from `render_safe_response` only
if all checks pass. The approved LLM draft remains in `draft_response`; it is
never copied into `final_response`. Revisions demonstrate the feedback loop and
gate publication, but do not personalize the official response. For this fixed
output contract, a deterministic baseline could return the policy message
directly without model calls.

`APPROVED` means the **text** passed review. A text explaining that human review
is required can pass without authorizing a refund. On exhaustion, the final status
is `REJECTED`, and no final response is published. A malformed evaluation counts
as rejection; provider failures propagate to the caller.

## Fictional rules

- Without a defect: up to 7 days after receipt.
- With a defect: up to 30 days after receipt.
- Eligible orders above 200,000 cents require human review.
- Missing or invalid receipt days, defect flag, or value produce `NEEDS_INFO`.

Amounts use integer `value_cents`. These rules do not represent Brazilian law.
Human review is only a policy outcome here; no human approval workflow is implemented.

## Run

From the repository root, using an environment with the repository dependencies:

```powershell
$env:LLM_MODEL = '<Groq model supporting tool calling>'
$env:GROQ_API_KEY = '<your key>'
venv/Scripts/python.exe 01-agent-orchestration/05-evaluator-optimizer/main.py
```

Configuration can also come from `.env`. Importing modules does not create a model
or call a provider. `build_graph(llm)` receives the model explicitly. Nodes call
the model directly; the evaluator uses `with_structured_output` with the local
Pydantic contract. No inner agent loop is needed.

The console uses `app.stream(..., stream_mode='updates')` to show each completed
node: policy result, draft and attempt number, evaluator verdict and feedback,
followed by the finalizer status. Each generated draft appears as `Tentativa N:`
before its evaluation. The final summary prints `Resposta oficial:` only when
approved; otherwise it requests manual review. This streams node updates, not
individual model tokens.

## Offline validation

```powershell
venv/Scripts/python.exe -m unittest discover -s 01-agent-orchestration/05-evaluator-optimizer/tests -v
```

Tests inject simulated responses and forbid network connections. They cover
approval, feedback retries, exhaustion, parsing errors, empty drafts, provider
failures, policy boundaries, deterministic rejection despite LLM approval,
finalizer revalidation, fixed official responses, configuration, and console output. They measure
software behavior, not real LLM quality. No separate mock CLI is provided.

Validation environment: Python 3.11.9, LangGraph 0.6.11, LangChain 0.3.30,
langchain-core 0.3.86,
langchain-groq 0.3.8, Pydantic 2.14.3. The repository requirements declare newer
LangChain versions; those versions and live Groq behavior were not validated
in this review. The model must support structured output through tool calling.

An LLM auditor can make mistakes. The attempt bound limits the outer workflow
to three generation/evaluation pairs (at most six model invocations with no
provider retries); it does not guarantee response correctness. Policies are
deterministic, while auditing clarity and policy compliance remains probabilistic.
The regex and phrase checks in `guardrails.py` are illustrative: they can miss
paraphrases and negated statements, so passing them does not prove semantic
correctness. Official responses use fixed templates independently of draft wording.

References: [LangGraph workflows](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
and [structured output](https://docs.langchain.com/oss/python/langchain/structured-output).
