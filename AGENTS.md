# AGENTS.md

## Objective
Using the existing architecture, pipeline, workflow, and project conventions already present in this repository, add **two external philosophy search providers**:

1. **Stanford Encyclopedia of Philosophy (SEP)** search component
2. **PhilPapers** search component

Do **not** redesign the system. Extend the current pipeline in the most architecture-consistent way possible. The current system already uses several search engines with various query and retrieval strategies for research quality, your job is to integrate SEP and PhilPapers as additional web search sources using the existing techniques.

---

## Core requirements

### 1) Preserve current architecture
- Reuse the repository’s existing pipeline, orchestration, service boundaries, data models, naming conventions, dependency injection patterns, and response formatting.
- Prefer extension over replacement.
- Avoid introducing parallel or redundant workflows if the current architecture already has a retrieval/search abstraction.

### 2) Add two provider integrations
Implement two source-specific search providers/adapters:

- `sep_search`
- `philpapers_search`

These should plug into the current retrieval/search layer the same way other sources/providers do, if such a layer already exists.

### 3) PhilPapers integration
PhilPapers appears to provide documented APIs. Use the official API/docs if accessible from the runtime environment.

Expected behavior:
- Search by query string
- Return normalized results
- Preserve source metadata
- Include canonical URL, title, authors if available, abstract/snippet if available, publication metadata if available, and source tag = `philpapers`

If authentication/API keys are required:
- read them from environment/config
- do not hardcode credentials
- document required env vars

### 4) SEP integration
SEP should be integrated as a search source, but **do not assume a public API exists**.
First, inspect the current official SEP search capabilities and determine the safest supported integration path.

Preferred order:
1. official API if it exists and is publicly supported
2. official search endpoint / OpenSearch-compatible path if supported
3. only if necessary and acceptable under site terms/robots, a minimal HTML search adapter

Expected behavior:
- Search by query string
- Return normalized results
- Preserve source metadata
- Include canonical URL, title, author if available, snippet if available, and source tag = `sep`

### 5) Unified normalized result schema
Map both providers into the repo’s existing internal schema. If no schema exists, create a minimal shared schema such as:

- `source`
- `title`
- `url`
- `authors`
- `summary`
- `published_at`
- `raw_source_metadata`

Keep provider-specific fields in a raw metadata field rather than polluting the shared interface.

### 6) Pipeline integration
Wire both providers into the current pipeline so they can participate in the same workflow as existing retrieval/search components.

Minimum desired behavior:
- selectable individually
- callable together in a multi-source search
- compatible with the current ranking / merging / formatting pipeline
- easy to disable via config if needed

### 7) Ranking and merging
If the repo already has ranking, deduplication, reranking, or merge logic:
- plug the new providers into that existing machinery
- do not create separate ranking logic unless absolutely necessary

If no such logic exists:
- return source-grouped results first
- keep implementation small and explicit

### 8) Configuration
Add provider configuration in the repo’s existing config style.

Examples of what may be needed:
- `PHILPAPERS_API_KEY`
- `PHILPAPERS_API_ID`
- `ENABLE_SEP_SEARCH=true`
- `ENABLE_PHILPAPERS_SEARCH=true`

Only add config that is actually needed by the implementation.

### 9) Tests
Add focused tests for:
- provider result parsing
- normalization into shared schema
- error handling / timeouts / empty results
- multi-provider aggregation if the repo supports it

Prefer small unit tests and narrow integration tests over giant theatrical nonsense.

### 10) Documentation
Update docs with:
- what was added
- required environment variables
- how to enable/disable each provider
- example usage
- any caveats about SEP access method
- any rate limit / authentication notes

---

## Implementation guidance

### First inspect before editing
Before making changes:
1. identify the current search/retrieval abstractions
2. identify existing provider/plugin patterns
3. identify config and env conventions
4. identify where result normalization should live
5. identify how tests are structured

Then implement using the repository’s existing patterns.

### Keep changes minimal and coherent
- Favor small, composable additions
- Avoid broad refactors unless they are required to fit the current architecture
- If an interface must change, make the smallest viable change and update all affected call sites

### Network behavior
- Use reasonable timeouts
- Handle upstream failures gracefully
- Return partial results if one provider fails and the system supports partial success
- Do not crash the whole pipeline because one philosophy source has a bad day

### Compliance and safety
- Respect official APIs, robots.txt, and site terms
- Prefer officially documented access methods over scraping
- If SEP does not provide a stable public API, implement the least brittle compliant search method and document the limitation clearly

---

## Deliverables
Complete the work with the following outputs:

1. provider implementation(s)
2. config/env additions
3. tests
4. docs updates
5. a concise implementation note summarizing:
   - where the providers were attached
   - whether SEP used an API, official search endpoint, or another compliant fallback
   - what config is required
   - any known limitations

---

## Non-goals
- Do not rebuild the entire architecture
- Do not add unrelated sources
- Do not introduce a giant framework detour just to perform two search integrations
- Do not hardcode credentials
- Do not silently scrape unsupported endpoints without documenting that choice
- Do not make any additional changes out of scope for SEP and Philpapers searches.