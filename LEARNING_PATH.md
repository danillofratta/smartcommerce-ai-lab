# SmartCommerce AI Lab — LEARNING_PATH

> **Trilha didática (PT-BR).** Metas baseadas em domínio técnico e evidências, não em quantidade de pastas. Nenhum item foi concluído automaticamente pela criação dos documentos.

## Regras do estudo

- Estudar **um laboratório de cada vez**. Não mudar para o próximo antes de executar no debugger e explicar as decisões.
- Cada laboratório deve mostrar: entrada → State → nós/tools → condições/loops → saída → testes → métricas → limitações.
- Analisar sempre a versão **sem IA** (baseline determinística) e o custo/benefício da IA.
- Para modo live: registrar modelo, provedor, prompt version, dataset, latência, tokens/custo (quando disponível) e amostra de erros.
- Para modo mock: registrar claramente que a execução é simulada e não é um benchmark do LLM.

## Sequência recomendada

### Fase 0 — Preparação e fundamentos
**Prioridade: agora**

- [ ] Criar repositório, venv, estrutura mínima e CLI simples.
- [ ] Definir o domínio SmartCommerce com fixtures sintéticas e políticas versionadas.
- [ ] `00_foundations/llm_vs_rules` — comparar roteamento com if/else e LLM.
- [ ] `00_foundations/structured_output` — Pydantic, parsing, retries, falhas.
- [ ] `00_foundations/mock_live_contract` — sem falsas execuções reais.

**Prova de aprendizado:** explicar input e output do LLM, schema, validação e divisão de responsabilidades.

### Fase 1 — Orquestração e ferramentas
**Prioridade: 1**

- [ ] `01_orchestration/sequential_chaining` — passagem de estado.
- [ ] `01_orchestration/intelligent_router` — conditional edges + decisão estruturada.
- [ ] `01_orchestration/react_tool_calling` — loop tools → LLM.
- [ ] `01_orchestration/parallel_fanout_fanin` — paralelismo e reducers.
- [ ] `01_orchestration/evaluator_optimizer` — feedback loop e limites.
- [ ] `01_orchestration/llm_supervisor` — supervisor LLM versus gerente determinístico.
- [ ] `01_orchestration/human_in_the_loop` — interrupt / resume / checkpoint.
- [ ] `01_orchestration/planner_executor_replanner` — ajuste de plano.
- [ ] `01_orchestration/hierarchical_subgraphs` — isolamento de estado e subgrafos.
- [ ] `01_orchestration/handoffs_vs_supervisor` — comparar autonomia e controle.

**Prova de aprendizado:** desenhar o grafo de memória, simular reprovação, explicar os limites de loops, comparar invoke/stream e lidar com falha de tool.

### Fase 2 — RAG + Evals (estudar em conjunto)
**Prioridade: 2; principal bloco de comparação**

- [ ] Criar corpus fictício de políticas/versionamentos de garantia, entrega e devolução.
- [ ] Criar dataset `refunds_v1` com perguntas simples, ambíguas, sem resposta e adversariais.
- [ ] `02_rag/naive_rag` + Evals de recuperação e grounding.
- [ ] `02_rag/hybrid_search` + comparação contra naive.
- [ ] `02_rag/reranking` + análise de ganho versus latência.
- [ ] `02_rag/metadata_filtering` + isolamento e vigência.
- [ ] `02_rag/multi_query` e `parent_document`.
- [ ] `02_rag/agentic_rag` + trajetória e limites.
- [ ] `02_rag/corrective_rag` e `self_rag`.
- [ ] `02_rag/graph_rag` (stretch após justificar utilidade).
- [ ] `03_evaluations/golden_datasets`, `deterministic_evals`, `llm_as_judge`, `rag_evals`, `regression_evals`.

**Prova de aprendizado:** responder se a técnica nova melhorou recuperação, fidelidade, custo e latência no mesmo dataset. Documentar casos em que piorou.

### Fase 3 — Ferramentas, conhecimento, memória e skills
**Prioridade: 3**

- [ ] `04_tools_mcp` — function tools, contratos, exceções, MCP server/client e permissões.
- [ ] `05_memory_context` — checkpoints, memória longa, sumarização, orçamentos, isolamento.
- [ ] `09_data_knowledge` — ingestão e atualização de documentos, chunking e índice versionado.
- [ ] `12_agent_skills` — skill selection, instruções reutilizáveis e carregamento progressivo.
- [ ] `14_analytics_sql` — agente analítico com consultas SQL **read-only** e limites.

**Prova de aprendizado:** distinguir dados persistidos, histórico de conversa, memória, índice vetorial, tools e skills. Demonstrar que uma tool não ignora permissões.

### Fase 4 — Segurança, confiabilidade e LLMOps
**Prioridade: 4**

- [ ] `06_guardrails_security` — prompt injection, exfiltração simulada, privilégio mínimo, tenants.
- [ ] `07_prompt_structured` — prompts versionados, schema robusto, regression set.
- [ ] `11_reliability` — retries, circuit breaker, idempotência, deadlines, durable execution.
- [ ] `08_observability_llmops` — tracing, métricas de custo, qualidade, comparação entre versões.
- [ ] `10_model_cost` — seleção de modelos, cache, limites de tokens, fallback.

**Prova de aprendizado:** recuperar workflow após falha, impedir ação duplicada e bloquear tentativa de induzir tool não autorizada. Registrar evidências verificáveis.

### Fase 5 — Expansão e produção
**Prioridade: 5**

- [ ] `13_multimodal` — nota fiscal sintética e avaliação de imagem de dano.
- [ ] `15_platform_delivery` — CLI → API, streaming, Docker, CI de testes/evals.
- [ ] `16_advanced_agents` — decisões hierárquicas, comparação com soluções simples.
- [ ] `17_model_adaptation` — RAG vs fine-tuning vs distillation (opcional e baseado em evidência).
- [ ] `18_ai_product_governance` — UX de handoff, métricas de produto, governança e documentação de risco.

**Prova de aprendizado:** demonstrar arquitetura, segurança, CI, regressão, custos e operação com evidências — não apenas um vídeo de demo.

## Cartão de progresso de um laboratório

| Campo | Valor a preencher |
|---|---|
| ID do lab | Ex.: `01_orchestration/intelligent_router` |
| Status | `PLANNED`, `IN_PROGRESS`, `VERIFIED`, `BLOCKED` |
| Conceito central | Ex.: roteamento LLM + grafo condicional |
| O que resolvo | Pedido do cliente → especialista correto |
| Baseline | Ex.: roteador por palavras-chave |
| Critério de aceitação | Ex.: 3 rotas cobertas, fallback seguro, 3 testes |
| Evidências | Saída CLI, testes, trace e avaliação quando aplicável |
| Minha explicação | Explicar State, edges, rota, erros e trade-offs |
| Desafio sem IA | Alterar a condição ou adicionar uma rota |

## Perguntas recorrentes para entrevistas

1. Por que usar um agente e não uma função determinística?
2. Qual é o contrato de State? O que persiste entre turnos e entre processos?
3. Quem decide: o LLM, um router determinístico ou uma política de negócio?
4. Como você limita loops, tempo, tokens e efeitos colaterais?
5. Como prova que a resposta RAG está baseada em documentos válidos?
6. Qual é a diferença entre tests, Evals, traces e monitoração?
7. Como evita replay duplicado, tool invocation insegura e vazamento entre clientes?
8. Quais trade-offs existem entre simplicidade, autonomia, latência, custo e qualidade?
9. Como escolhe entre retrieval, fine-tuning e prompt design?
10. Como sabe se uma mudança de modelo/prompt melhorou o sistema?

## Próximo passo

Criar o repositório e iniciar **apenas** `00_foundations/structured_output` ou `01_orchestration/intelligent_router`. Validar no debugger e com testes antes de avançar. A ferramenta de IA pode auxiliar na implementação, mas a conclusão depende de entendimento demonstrável.
