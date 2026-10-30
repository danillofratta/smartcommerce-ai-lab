# SmartCommerce AI Lab — PROJECT_CONTEXT

> **Documento canônico de contexto e continuidade.** Anexe este arquivo ao novo projeto do ChatGPT e mantenha-o atualizado quando uma decisão importante mudar.
>
> **Estado em 30/10/2026:** planejamento aprovado; **nenhum laboratório está implementado ou validado por este pacote**.

## 1. Identidade e missão

- **Nome:** SmartCommerce AI Lab
- **Descrição pública:** *Learn AI Engineering by building, testing and comparing production-oriented AI systems in one fictional commerce domain.*
- **Objetivo primário:** aprender profundamente **conceitos, implementação, depuração, avaliação e trade-offs** de engenharia de IA.
- **Objetivo secundário:** construir portfólio público de qualidade para posições de Senior/Staff AI Engineer e Software Architect.
- **Método:** laboratórios pequenos, independentes, didáticos e comparáveis. Não criar um aplicativo de e-commerce completo antes de dominar os conceitos.
- **Idioma:** documentação pública `README.md` em inglês; explicações didáticas e material de estudo em português. Código, APIs e nomenclatura preferencialmente em inglês.
- **Usuário/programador:** o proprietário do repositório deve compreender, executar no debugger, alterar e explicar cada implementação — não apenas aceitar código de IA.

## 2. Domínio de negócio comum: loja virtual fictícia

Uma loja fictícia vende eletrônicos. Existem clientes, catálogo, estoque, pedidos, pagamentos, entregas, suporte, garantias, devoluções e reembolsos.

**Casos de uso que se repetem entre laboratórios** (para que seja possível comparar técnicas sem mudar o problema):

1. `ROUTE-001`: "Meu PIX não chegou; onde está meu pedido?" → classificar/rotear para as áreas certas.
2. `ORDER-001`: "Qual é o status do pedido 1024?" → consultar tools e interpretar respostas.
3. `REFUND-001`: "Quero devolver meu notebook comprado há 18 dias" → recuperar políticas fictícias, verificar elegibilidade e justificar.
4. `REFUND-002`: "Quero reembolso de R$ 2.500" → avaliar necessidade de aprovação humana; **nunca mover dinheiro de verdade**.
5. `INCIDENT-001`: "Fui cobrado duas vezes e a entrega está atrasada" → coordenar múltiplas equipes e ferramentas.
6. `POLICY-001`: "Posso devolver um notebook em promoção com embalagem aberta?" → RAG, citações e avaliações.
7. `INVOICE-001`: extração estruturada de uma nota fiscal **sintética** → multimodal/document AI.
8. `ANALYTICS-001`: "Quais pedidos tiveram atraso nesta semana?" → analytics/Text-to-SQL com banco de leitura fictício.

**Dados e políticas:** fixtures sintéticas, estáveis, versionadas; IDs fictícios; regras de reembolso inventadas exclusivamente para o laboratório. Não afirmar que elas representam legislação brasileira. Valores financeiros representados em centavos (inteiros) e operações tratadas com regras determinísticas. Dados sensíveis ou credenciais jamais incluídos nos commits.

## 3. Princípios não negociáveis

1. **Mesmo domínio, padrões diferentes.** Cada laboratório deve ensinar uma habilidade nova, não apenas renomear agentes.
2. **Um laboratório = uma pergunta central.** Explicar problema, arquitetura, State, nodes, edges, fluxo, testes e limitações.
3. **Começar simples.** Primeiro baseline determinístico ou LLM único; acrescentar agentes somente quando houver benefício verificável.
4. **Autonomia controlada.** O LLM pode classificar, propor, resumir ou planejar; autorização, regras financeiras e efeitos colaterais ficam no código do sistema.
5. **Modo mock e live.** Mock sem rede/sem custo, com decisões explícitas e reproduzíveis; live executa chamadas reais e falha claramente se faltar configuração. Mock jamais deve fingir uma avaliação estatística de modelo real.
6. **Testes e Evals não são a mesma coisa.** Pytest valida software e invariantes; Evals medem tarefas, qualidade, uso de tools, grounding, regressão, latência e custo.
7. **Observabilidade ≠ persistência.** Console logging, tracing e checkpointing têm propósitos separados.
8. **Foco em execução local.** CLI primeiro. Evitar frontend, microsserviços e infraestrutura complexa até aparecer necessidade educativa concreta.
9. **Versionamento e reprodutibilidade.** Versões de dependências, prompts, modelos, fixtures, políticas e datasets registradas.
10. **Não avançar sem compreensão demonstrada.** Cada laboratório passa por explicação → implementação → debug → testes → avaliação → documentação → desafio manual.
11. **Sem overengineering compartilhado.** Compartilhar somente o domínio sintético, fixture loaders, contratos realmente transversais, configuração e telemetria. State e grafo pertencem a cada laboratório.
12. **Não inventar métricas.** Relatórios públicos devem diferenciar dados reais, resultados simulados e hipóteses.

## 4. Tecnologias propostas (não instaladas nem verificadas nesta fase)

- Python 3.12+ (confirmar versão do ambiente antes de fixar).
- LangGraph + LangChain Core para workflows e grafos; Pydantic para validação e saídas estruturadas.
- Groq / ChatGroq como **primeiro** provedor LLM; modelo configurável em `.env`; sem hardcode de identificador.
- Langfuse opcional para tracing, datasets e experimentos; validar integração com versões efetivamente instaladas.
- Pytest para testes; ferramentas de lint/typing simples.
- Dados locais em JSON/Markdown e SQLite. Banco vetorial ou PostgreSQL/pgvector apenas quando o laboratório exigir comparação real.
- MCP com SDK atualizado quando chegar ao módulo correspondente.
- Ragas ou avaliadores próprios apenas quando métricas concretas justificarem a dependência.
- Docker, FastAPI, OTEL, pipelines CI e deployment somente nos módulos adequados.
- Caso comparações entre frameworks sejam realizadas no futuro, usar mesmos casos/datasets e distinguir o runtime. O foco principal inicial é LangGraph.

**Antes de programar:** consultar documentação oficial atual para confirmar APIs, versão e compatibilidade. Evitar copiar exemplos depreciados.

## 5. Catálogo de competências e laboratórios

### 00 — AI foundations & baselines [CORE]
- `llm_vs_rules`: quando usar regras, LLM ou híbrido.
- `structured_output`: Pydantic, schema, erros e validação.
- `single_agent`: agente simples com State e histórico.
- `mock_live_contract`: separar simulação e chamadas reais.

### 01 — Agent orchestration [CORE]
1. `sequential_chaining`: vendas → orçamento → atendimento.
2. `intelligent_router`: atendimento → financeiro/pedidos/vendas/suporte.
3. `react_tool_calling`: consultar pedido e pagamento iterativamente.
4. `parallel_fanout_fanin`: estoque, fraude fictícia e entrega em paralelo.
5. `evaluator_optimizer`: proposta de reembolso → auditor → feedback loop.
6. `llm_supervisor`: supervisor escolhe especialista dinamicamente, com limites externos.
7. `human_in_the_loop`: reembolso simulado com autorização e retomada.
8. `planner_executor_replanner`: plano de resolução de incidente de pedido.
9. `hierarchical_subgraphs`: supervisor → equipes financeira e operacional.
10. `handoffs_vs_supervisor`: comparar transferência de controle com controle centralizado.

### 02 — RAG engineering [CORE]
1. `naive_rag`: chunks, embeddings, retrieval, resposta com fonte.
2. `hybrid_search`: busca vetorial + lexical/BM25.
3. `reranking`: recuperar muitos → reordenar poucos.
4. `multi_query`: múltiplas reformulações de pergunta.
5. `parent_document`: chunks pequenos e contexto pai.
6. `metadata_filtering`: políticas por categoria, vigência e acesso.
7. `agentic_rag`: agente escolhe fontes/tools e verifica suficiência.
8. `corrective_rag`: detectar recuperação ruim e tentar novamente.
9. `self_rag`: decidir necessidade de busca e criticar groundedness.
10. `graph_rag`: relacionamentos entre pedido, produto, política e entidade (stretch).

### 03 — AI evaluations & testing [CORE]
1. `golden_datasets`: casos com resposta/rota/tools esperadas.
2. `deterministic_evals`: invariantes e verificações sem LLM.
3. `llm_as_judge`: rubricas, calibração e limites.
4. `rag_evals`: relevância, precision/recall, groundedness/faithfulness.
5. `trajectory_evals`: tool selection, argumentos e sequência de ações.
6. `regression_evals`: comparar prompt/modelo/versão de estratégia.
7. `experiments_ab`: custos/qualidade/latência com casos comparáveis.
8. `online_evals`: monitoramento de traces fictícios e análise de falhas.
9. `adversarial_dataset`: casos fora de escopo, tentativas de manipulação.

### 04 — Tools, function calling & MCP [CORE]
- `simple_tools`, `tool_retries`, `parallel_tools`, `tool_contracts_validation`.
- `mcp_server`, `mcp_client`, `mcp_permissions`.
- Estudar diferença entre uma tool, um MCP server, um agente e uma skill. Aprovação humana antes de ações com efeitos colaterais.

### 05 — Memory & context engineering [CORE]
- `short_term_checkpoints`, `long_term_memory`, `summarization`, `context_selection`, `token_budget`, `memory_isolation`.
- Recuperação seletiva, TTL/retenção, minimização e exclusão de informações fictícias.

### 06 — Guardrails, security & Responsible AI [CORE]
- `input_scope`, `output_validation`, `prompt_injection`, `tool_authorization`, `tenant_isolation`, `pii_redaction`, `unsafe_tool_args`, `red_team_suite`.
- A defesa principal é a autorização programática e o menor privilégio, não apenas prompt de segurança.
- Referência a considerar: **OWASP GenAI LLM Top 10 2026**.

### 07 — Prompt engineering & structured generation [CORE]
- `zero_few_shot`, `schema_contracts`, `prompt_versioning`, `prompt_injection_resistance`, `prompt_comparisons`.
- Estudos devem medir qualidade por datasets; não aceitar melhora por sensação pessoal.

### 08 — Observability & LLMOps [CORE]
- `console_logging`, `langfuse_tracing`, `token_cost_tracking`, `trace_evals`, `experiment_dashboards`, `release_regression_gate`.
- Distinguir trace, span, geração, log, score, checkpoint e metric.

### 09 — Data & knowledge engineering [HIGH]
- `document_ingestion`, `chunking_strategies`, `embedding_selection`, `index_versioning`, `incremental_updates`, `freshness_deletion`, `metadata_acl`.
- Explicar lineage e impacto das mudanças de política na qualidade do RAG.

### 10 — Model selection, inference & cost engineering [HIGH]
- `model_comparison`, `temperature_and_sampling`, `provider_fallback`, `rate_limits`, `caching`, `token_budgeting`, `quality_cost_frontier`.
- Comparar modelos pela tarefa; não assumir que modelo maior sempre vence.

### 11 — Reliability & durable execution [HIGH]
- `timeouts_retries`, `bounded_loops`, `checkpoints_resume`, `idempotent_tools`, `concurrency`, `error_recovery`, `compensation_simulation`.
- Simular replay, falha no meio do workflow e retomada sem duplicar ações.

### 12 — Agent skills & reusable capabilities [HIGH]
- `skill_definition`, `skill_selection`, `progressive_disclosure`, `skill_with_tools`, `skill_security`.
- Distinguir instrução reutilizável, tool, workflow e knowledge base.

### 13 — Multimodal & document intelligence [HIGH]
- `invoice_extraction`, `product_damage_image`, `ocr_vs_vision_llm`, `multimodal_evals`.
- Somente dados e imagens sintéticos ou licenciados para uso público.

### 14 — Data analytics & safe Text-to-SQL [HIGH]
- `read_only_sql_agent`, `schema_retrieval`, `sql_validation`, `analytics_reporting`, `sql_evals`.
- Banco SQLite fictício e **somente leitura**; bloquear SQL mutável, consultas excessivas e acesso fora de escopo.

### 15 — Production platform & delivery [HIGH]
- `fastapi_wrapper`, `async_streaming`, `docker_compose`, `ci_tests_evals`, `deployment_config`, `privacy_and_secrets`, `otel_integration`.
- Só depois que laboratórios locais estiverem reproduzíveis e compreendidos.

### 16 — Advanced agent systems [STRETCH]
- `hierarchical_planning`, `multi_agent_collaboration`, `dynamic_model_routing`, `multi_step_research`, `distributed_execution_comparison`.
- Exigir justificativa de complexidade, segurança e Evals comparativos.

### 17 — Model adaptation, fine-tuning & distillation [STRETCH]
- `prompt_vs_rag_vs_finetune`, `small_model_distillation`, `dataset_quality`, `adapter_experiment`.
- Entrar somente quando houver dataset e hipótese mensurável; não fine-tunar por modismo.

### 18 — AI product engineering & governance [STRETCH]
- `human_handoff_ux`, `uncertainty_citations`, `feedback_collection`, `policy_versions`, `model_risk_register`, `cost_slo`.
- Inclui UX de agentes, explicabilidade prática, governança, retenção e métricas de produto.

**Os rótulos CORE / HIGH / STRETCH são prioridades, não promessa de implementar todos simultaneamente.** Um módulo pode conter subexemplos, mas cada subexemplo só vira laboratório quando houver objetivo, fixture, testes e DoD definidos.

## 6. Organização alvo (estrutura planejada)

```text
smartcommerce-ai-lab/
├── README.md                    # apresentação pública em inglês
├── PROJECT_CONTEXT.md           # documento canônico para continuidade
├── LEARNING_PATH.md             # fases, prioridades, práticas e competências
├── LAB_TEMPLATE.md              # contrato de documentação de cada lab
├── lab.py                       # CLI futura (ainda não implementada)
├── labs/
│   ├── 00_foundations/
│   ├── 01_orchestration/
│   ├── 02_rag/
│   ├── 03_evaluations/
│   ├── 04_tools_mcp/
│   ├── 05_memory_context/
│   ├── 06_guardrails_security/
│   ├── 07_prompt_structured/
│   ├── 08_observability_llmops/
│   ├── 09_data_knowledge/
│   ├── 10_model_cost/
│   ├── 11_reliability/
│   ├── 12_agent_skills/
│   ├── 13_multimodal/
│   ├── 14_analytics_sql/
│   ├── 15_platform_delivery/
│   ├── 16_advanced_agents/
│   ├── 17_model_adaptation/
│   └── 18_ai_product_governance/
├── smartcommerce/               # domínio e fixtures sintéticas reutilizáveis
│   ├── fixtures/
│   ├── policies/
│   ├── models/
│   └── tools/
├── benchmarks/
│   ├── datasets/
│   ├── evaluators/
│   └── reports/
├── tests/
└── docs/
    ├── architecture/
    ├── decisions/
    └── progress/
```

Não criar todas as pastas vazias de uma vez. Criar somente o que for implementado/validado a cada etapa.

## 7. Contrato mínimo de execução e comparação

**CLI planejada, ainda não existente:**

```bash
python lab.py list
python lab.py run orchestration/router --mode mock --case ROUTE-001
python lab.py run orchestration/router --mode live --case ROUTE-001
python lab.py graph orchestration/router
python lab.py eval rag --dataset refunds_v1 --mode live
```

Cada lab deve ter:
- entrada conhecida e output claro; execução isolada; modo mock quando viável;
- `State` explícito (se usar LangGraph), nodes, edges e Mermaid;
- casos de sucesso, falha e limite; logs de roteamento/ciclos;
- testes offline reproduzíveis; métricas reais quando for pertinente;
- texto que indique se a evidência é mock, live, medida ou não medida;
- exemplos que nunca dependam de serviços reais de pagamento.

O CLI central só padroniza descoberta/execução; não deve esconder o que os nós realmente fazem.

## 8. Definition of Done (DoD) de um laboratório

Um laboratório só é considerado **concluído** quando:

- [ ] Problema e hipótese definidos; justificativa para usar IA ou não.
- [ ] Grafo/fluxo desenhado, State e contratos compreendidos.
- [ ] Implementação e dependências reproduzíveis; código curto o suficiente para estudar.
- [ ] Modo mock testado; modo live testado se o laboratório exigir LLM e houver credenciais.
- [ ] Casos de sucesso, erro, limite e segurança cobertos por pytest.
- [ ] Debug passo a passo registrado (qual nó, estado inicial/final, qual decisão e por quê).
- [ ] Eval/dataset registrado quando aplicável; não inventar score.
- [ ] README didático do laboratório e diagrama Mermaid revisados.
- [ ] Proprietário consegue explicar em palavras próprias e modificar uma regra sem IA.
- [ ] Commit pequeno e claro; nenhuma chave ou arquivo sensível versionado.

## 9. Protocolo de trabalho em conversas futuras

Quando este documento for anexado a um novo projeto do ChatGPT:

1. Trate-o como fonte principal de objetivos, domínio, nomenclatura e prioridades, mas confirme o estado REAL do código antes de afirmar que algo foi implementado.
2. **Não implemente todos os laboratórios de uma vez.** Trabalhe em uma etapa por vez e pare após validação. Não avançar de módulo sem entendimento.
3. Ao começar um lab, primeiro apresentar desenho do fluxo, responsabilidades de cada nó, contratos de estado, casos de teste e trade-offs em linguagem simples.
4. Ao revisar código, apontar onde o LLM decide, onde o código decide e quais são os pontos de falha.
5. Usar SDD leve: proposta curta → critérios de aceitação → implementação mínima → testes/evals → revisão → documentação.
6. Preferir exercício no debugger e perguntas progressivas antes de entregar soluções complexas prontas.
7. Não presumir acesso ao repositório nem execução local; solicitar arquivos/saídas apenas quando forem necessários para verificar algo.
8. Priorizar Python/LangGraph/Groq/Langfuse inicialmente; mudar tecnologias por necessidade comprovada, não por hype.
9. Novas competências podem ser adicionadas, mas exigir motivação, cenário SmartCommerce, exercício e critério de avaliação.
10. Manter `docs/progress/STATUS.md` (quando criado) e este arquivo atualizados a cada marco validado, com status PLANNED / IN_PROGRESS / VERIFIED / BLOCKED.

## 10. Primeira entrega (Milestone 0)

**Objetivo:** criar estrutura mínima do repositório e escolher o primeiro lab para aprender, sem tentar construir tudo.

1. Criar repositório local `smartcommerce-ai-lab`.
2. Adicionar estes quatro documentos; usar `PROJECT_CONTEXT.md` no ChatGPT Project.
3. Definir fixtures pequenas e 3–5 casos de teste, totalmente fictícios.
4. Validar versões de Python e dependências antes de instalar.
5. Construir primeiro lab: `00_foundations/structured_output` **ou** `01_orchestration/intelligent_router`, conforme escolha do aluno.
6. Executar com mock e live, acompanhar State no debugger e escrever 3 testes básicos.
7. Só então ampliar os módulos.

**Critério de sucesso do Milestone 0:** o aluno consegue explicar a arquitetura planejada e executar **um** laboratório pequeno de ponta a ponta; documentos sozinhos não significam esse marco concluído.

## 11. Referências técnicas para consultar na implementação

- LangChain/LangGraph learning & patterns: https://docs.langchain.com/oss/python/learn
- LangGraph concepts: https://docs.langchain.com/oss/python/langgraph/overview
- Langfuse evaluation & experiments: https://langfuse.com/docs/evaluation/overview
- Ragas metrics: https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/
- MCP specification: https://modelcontextprotocol.io/specification
- OWASP GenAI LLM Top 10 (edição 2026): https://github.com/GenAI-Security-Project/GenAI-LLM-Top10
- OpenAI Agents SDK (referência comparativa; não substitui o foco em LangGraph): https://developers.openai.com/api/docs/guides/agents/sdk

---

**Regra central:** não colecionar exemplos; desenvolver competência demonstrável com código, testes, métricas e explicação independente.
