# Personal Context — Roadmap

**Status:** vivo · **Atualizado:** 2026-08-26  
Tese e demo para a comunidade: [`docs/VISION.md`](VISION.md).  
Isto **não** é spec Speckit. Um epic por vez vira `specs/<nnn>-<nome>/` via `/speckit-specify` → plan → tasks → implement.

---

## Princípios

1. **Contexto é da pessoa.** Nenhum runtime é dono.
2. **Memória ≠ contexto.** Guardar tudo não é entender a situação.
3. **Contexto é temporal.** Fatos, preferências e estados mudam; o histórico não some.
4. **Proveniência importa.** Sem fonte, não é canônico.
5. **Context quality > context volume.** Mais contexto não significa melhor contexto.
6. **Mínimo privilégio.** O agente recebe o necessário para a tarefa, não o vault inteiro.
7. **Controle explícito.** Correção da pessoa vence inferência do agente.
8. **Agnóstico a modelo.** MCP primeiro; adapters de runtime depois.
9. **Local-first.** Ler, editar e buscar funciona offline. Vault cifrado, loopback.
10. **Importado é dado, nunca instrução.** E-mail, calendário e plugins não ampliam grant nem disparam ação.
11. **Propriedades transversais.** Identity, privacy, provenance e policy acompanham todas as camadas.

Não construir: modelo de fundação próprio; vector DB como produto; runtime de agente próprio; agente pessoal que planeja e age sozinho; ingestão universal de “tudo que a pessoa já fez”; grafo obrigatório em graph database; protocolo A2A novo. Horizonte ou recusa até revisão deste documento.

---

## Vocabulário (colisões)

No Hub atual, dois nomes **não** são as primitivas da Layer:

| Termo da Layer | O que o Hub já tem | Não confundir |
|----------------|--------------------|---------------|
| **State** (condição operacional: *Planning*, *Comparing itineraries*) | `SharedState` = handoff com TTL | Não rebatizar SharedState. State entra em E3. |
| **Intent** (o que a pessoa está tentando fazer agora) | `ActionIntent` = aprovação de ação externa | Não rebatizar ActionIntent. Intent de situação entra em E3. |
| **Skill** (capacidade reutilizável) | `MemoryKind.procedural` | Objeto Skill é horizonte; o engine precisa provar a necessidade primeiro. |

Três camadas que o produto mistura com frequência:

```text
Memory     — informação persistida.  "I said I wanted to visit Amsterdam."
Context    — recorte relevante agora. User is planning a 10-day Europe trip; Amsterdam is a candidate; budget-sensitive.
Situation  — frame operacional.      Project: Europe Trip; Goal: plan 10-day trip; State: comparing itineraries; Intent: choose next itinerary.
```

> **Memory is persisted information. Context is the relevant information for a situation. Situation is the operational frame in which an agent is acting now.**

Primitivas conceituais da Layer (nem todas precisam ser entidades persistentes no dia um; algumas começam derivadas pelo engine): Identity, Memory, State, Goals, Preferences, Relationships, Projects, Skills, Intent, Provenance.

---

## O que 001–003 entregaram

Capítulos fechados. Não reabrir como epic. Evoluir só via spec filha.

**001 — Personal Context Hub.** Vault cifrado, schema, UI, pairing, grants, propostas de memória, aprovações, auditoria append-only, busca, brief de projeto, export/import PCA, MCP (`search_personal_context`, `get_context_manifest`, `propose_memory`, shared state, ações).

Primitivas atuais: Person, Profile, Preference, Project, Goal, Commitment, Decision, Memory, Artifact, SharedState, Provenance.

**002 — Conectores.** Assistente real (Cursor) via receita MCP; calendário (`private`); Gmail seletivo (`sensitive`); claims de assistente somente por proposta; Hub não extrai sozinho.

**003 — Plugins e marketplace.** Kernel separado de convidados isolados. Plugins: Calendar, Gmail, RSS. Kit: `pcl-sdk plugin` (sideload e catálogo).

### O que ainda não são

O Hub guarda, filtra, busca, propõe e apresenta briefs/manifests. Ainda não monta, de forma geral:

> **What does this agent need to know about this person, for this task, right now?**

Também faltam: validade temporal; estado operacional de projeto; intent de situação; grafo tipado; adapters além de Cursor/demo-agent; avaliação sistemática de qualidade do contexto.

---

## Mecanismo (uma vez)

O Context Engine existe para responder, antes que o agente aja:

1. What does this agent need to know?
2. What is relevant to the current situation?
3. What is still true?
4. What is historical?
5. What is inferred?
6. What is authoritative?
7. What can this agent access?
8. What should remain hidden?
9. What changed since the last interaction?
10. What context should be carried forward?

Objetivo: **o menor contexto suficiente para a situação.** Source ≠ Truth: uma fonte pode estar errada, stale, incompleta ou ser só inferência. Provenance, confidence, authority e freshness entram no recorte. Cada source opera dentro de um grant — ter conector não coloca o dado em qualquer contrato.

**Context Contract** — unidade que o agente recebe. Ele não precisa saber onde os dados moram.

```text
Context Contract
  Subject / Situation / Intent
  Required context (goals, preferences, decisions, project state, …)
  Granted scope     (personal, travel, project:123, …)
  Omitted           (projetos alheios, work privado, …)
  Provenance / Freshness / Confidence
```

**Context Quality** — maximizar Relevant + Current + Authorized + Sufficient. Métricas futuras: o contexto certo foi recuperado? vazou irrelevante? estava fresco? conflitos resolvidos? o agente teve o suficiente? quanto contexto foi preciso para melhorar a tarefa?

**Context Debt** — conceito futuro, não MVP. Como technical debt: itens stale, preferências em conflito, projetos abandonados, inferências nunca confirmadas, dados sem provenance, duplicação, autoridade pouco clara. “Context Health” (freshness, provenance, conflicts, stale, unverified) só faz sentido com escala.

**Isolamento (segunda demo).** Portability without indiscriminate sharing: Personal Agent vê scope pessoal; Work Agent não recebe contexto pessoal que não precisa. A tese não é “um dump para todos os agentes”.

---

## Próxima era — E1–E6

Fila ordenada. Um epic por vez vira spec. Cada spec filha deve ser testável sozinha. A próxima era prova a killer demo em [`VISION.md`](VISION.md).

```text
001 Hub → 002 Connectors → 003 Plugins
        → E1 Context Engine
        → E2 Temporal → E3 Situation/State/Intent → E4 Graph → E5 Adapters → E6 Evaluation
        → (horizonte) Personal Intelligence → Personal Agency
```

### E1 — Context Engine

**Spec:** `specs/004-context-engine/`

**Problema.** O agente precisa saber o que buscar. O Hub devolve hits e briefs, mas ainda não produz um pacote completo da situação.

**Resultado.** Pedido com intent + recorte necessário → Context Contract contendo: objetivo; preferências; memórias relevantes; restrições; estado disponível; citações/provenance; escopo concedido; informação deliberadamente omitida. A demo “continue planning the trip” deve funcionar usando objetos que já existem em 001.

**Cabe.** Context Query; context read; relevance ranking; context assembly; recorte por grant; Context Contract.

**Não cabe.** Inferência automática a partir de e-mail; vector DB; Personal Intelligence; Personal Agency.

**Depende de.** 001–003.

### E2 — Validade Temporal

**Spec:** —

**Problema.** Preferências e fatos mudam. Hoje existe versão e retention, mas ainda não há representação clara de “o que vale agora” vs “o que foi verdade”.

**Resultado.** `"I didn't like X."` → `"I now like X."` As duas permanecem; o engine devolve a vigente.

**Cabe.** `valid_from`; `valid_until`; resolução vigente vs histórico; filtro temporal no E1.

**Não cabe.** Merge semântico sofisticado; esquecimento automático sem política.

**Depende de.** E1.

### E3 — Estado de Projeto e Intent de Situação

**Spec:** —

**Problema.** `SharedState` é handoff com TTL. `ActionIntent` é aprovação. Falta representar fases (`Planning`, `Comparing itineraries`, `Waiting for approval`, `Choosing hotel`) e “o que a pessoa está tentando fazer agora?”.

**Resultado.** O Context Contract inclui fase atual, passo corrente, intent curto e estado operacional.

**Cabe.** Estado operacional de Project/Goal; intent de situação; visibilidade para a pessoa; separação de memória durável.

**Não cabe.** Rebatizar SharedState; rebatizar ActionIntent; planner autônomo.

**Depende de.** E1.

### E4 — Grafo Leve

**Spec:** —

**Problema.** Relacionamentos hoje são principalmente FKs. Não há relações tipadas (`owned_by`, `depends_on`, `blocked_by`, `related_to`).

**Resultado.** O Context Engine inclui relações úteis no Context Contract (ex.: Project A → depends_on → Project B → blocked_by → Person C).

**Cabe.** Relações tipadas; consulta a partir de objeto âncora; respeitar grants.

**Não cabe.** Graph database; A2A; social graph.

**Depende de.** E1.

### E5 — Adapters de Runtime

**Spec:** —

**Problema.** A tese é portabilidade. Hoje o cliente real é Cursor, com demo-agent e um segundo runtime de teste.

**Resultado.** Pelo menos dois runtimes de uso real consomem o mesmo Context Contract. Candidatos: Hermes, OpenClaw. O usuário troca de runtime sem reeditar o contexto.

**Cabe.** Receitas por runtime; pairing; catálogo; contrato MCP existente; validação da killer demo.

**Não cabe.** Adapter por modelo quando o runtime já fala MCP; protocolo novo.

**Depende de.** E1.

### E6 — Avaliação de Qualidade de Contexto

**Spec:** —

**Problema.** Ainda não medimos se o recorte está correto, fresco, preciso ou barato.

**Resultado.** Conjunto pequeno de casos: killer demo; conflito temporal; isolamento de contexto; troca de runtime. Métricas: context retrieval accuracy; context precision; freshness; conflict resolution; portability; user correction rate; context assembly cost.

**Cabe.** Harness; casos fixos; critérios observáveis.

**Não cabe.** Benchmark público; otimização de tokens como produto.

**Depende de.** E1; ganha força com E2 e E5.

---

## Horizonte

Nomeados. Não entram na fila até promoção à próxima era.

| Tema | Por que esperar |
|------|-----------------|
| Skills como primitiva | Procedural memory já existe; objeto Skill só depois que o engine provar necessidade de descoberta/recorte. |
| Ciclo Observe → Extract → Classify → Consolidate | O Hub decidiu que assistentes propõem; extração interna é outro produto. |
| Personal Intelligence | Precisa de contexto estável e confiável. *Without reliable context, intelligence predicts from noise.* |
| Personal Agency | Precisa de contexto montado, policy e autorização. |
| A2A / Context Agent | MCP atende à próxima era. |
| Context Debt / Context Health | Só faz sentido com escala suficiente de contexto. |
| Anticipatory AI | Só depois que Personal Intelligence demonstrar valor real. |

A próxima era termina quando o sistema entregar: **the right context, to the right agent, for the right situation, at the right time — under the user's control.**

---

## A escada (horizonte, não o produto)

```text
Memory → Personal Context → Context Engine → Personal Intelligence → Personal Agency
```

Atravessam todas as camadas: Identity, Privacy, Provenance, Policy, User Ownership, Interoperability.

**Memory** — *AI remembers what happened.* Armazenar, atualizar, recuperar, esquecer.  
**Personal Context** — *AI understands what matters about the person.* Memory responde “o que aconteceu?”; Context responde **“o que importa para esta situação?”**  
**Context Engine** — *AI assembles the right context for the situation.* É a próxima era.  
**Personal Intelligence** — *AI understands patterns across the person's context.* Padrões, conflitos, necessidades prováveis, próximos passos. Só depois de um engine confiável. Não é mais recuperar informação: é raciocinar sobre a representação da pessoa.  
**Personal Agency** — *AI plans and acts continuously on behalf of the person.* Context → Understand → Predict → Plan → Act, com feedback de volta ao contexto. Qualquer ação externa continua subordinada a identity, grants, policy, approval e audit. **Não faz parte da próxima era.**

---

## Como usar estes arquivos

- **Agente implementando feature:** se não há spec em `specs/`, não inventar epic a partir da visão. Apontar o epic neste roadmap e pedir `/speckit-specify`.
- **Agente em dúvida de produto:** tese e contrastes em [`VISION.md`](VISION.md) vencem vector DB, agente autônomo, marketplace de ações.
- **Pessoa dona do repo:** somente um epic da fila vira spec ativa. Completou → marca Spec → passa ao próximo.
- **Constituição Speckit:** copiar os princípios quando a constitution for preenchida; não transformar este roadmap em spec.

## Speckit (quando um epic estiver maduro)

1. `/speckit-specify` com o recorte do epic, **não** o documento de visão.
2. Preencher o campo **Spec** do epic com o caminho (`specs/<nnn>-…`).
3. Seguir `plan → tasks → implement` somente nessa spec filha.

A origem da tese é o rascunho `personal-context-layer-spec.md`. O Hub (specs 001–003) já é a forma de produto dessa tese, local-first.

## Changelog

- **2026-08-26** — Gauntlet round 2 — VISION.md é só a espinha compartilhavel; este arquivo guarda operação.
- **2026-08-26** — Gauntlet round 1 — shareable spine; architecture after the fold.
- **2026-08-26** — Primeira versão do roadmap: tese, 001–003 como passado, E1–E6 como próxima era, horizonte explícito.
- **2026-08-26** — Evolução conceitual: Product Evolution, Context Problem, Situation, Context Contract, Context Quality, Context Isolation, Personal Intelligence e Personal Agency como camadas explícitas da visão.
