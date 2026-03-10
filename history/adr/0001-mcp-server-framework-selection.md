# ADR-0001: MCP Server Framework Selection

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-03-09
- **Feature:** 002-silver-tier
- **Context:** Silver tier requires an MCP (Model Context Protocol) server for automated email sending via Gmail API. The system must integrate with Claude Code for AI-driven email composition and execution. Initial research suggested FastMCP (Python) for consistency with the Bronze tier Python stack, but PROJECT_REFRENCE.md specifies Node.js v24+ as a prerequisite, indicating the official TypeScript MCP SDK is the intended framework.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Adds Node.js to Python project, affects deployment and maintenance
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - FastMCP (Python) vs TypeScript SDK vs custom implementation
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects MCP server implementation, dependencies, integration patterns
-->

## Decision

Use the official **TypeScript MCP SDK** (`@modelcontextprotocol/server`) with Node.js for the email sending MCP server.

**Technology Stack**:
- **Framework**: @modelcontextprotocol/server (official Anthropic SDK)
- **Language**: TypeScript for type safety and MCP protocol compliance
- **Runtime**: Node.js v24+ (per PROJECT_REFRENCE.md prerequisite)
- **Transport**: StdioServerTransport for local Claude Code integration
- **Gmail Integration**: googleapis npm package for Gmail API access
- **Build**: TypeScript compiler (tsc) with build script

**Project Structure**:
- Separate Node.js project in `mcp_servers/email_sender/` with own package.json
- TypeScript source in `src/` directory
- Compiled JavaScript output for execution

## Consequences

### Positive

- **Official Support**: Uses Anthropic's official MCP SDK with active maintenance and documentation
- **Type Safety**: TypeScript provides compile-time type checking for MCP protocol compliance
- **Ecosystem Alignment**: Follows PROJECT_REFRENCE.md architecture requirements (Node.js v24+ prerequisite)
- **Rich Tooling**: Access to Node.js ecosystem for Gmail API integration (googleapis package)
- **Protocol Compliance**: Official SDK ensures correct MCP protocol implementation (tool registration, stdio transport, error handling)
- **Future-Proof**: Aligned with Anthropic's recommended approach for MCP server development

### Negative

- **Multi-Language Stack**: Introduces Node.js/TypeScript alongside Python, increasing complexity
- **Additional Dependencies**: Requires Node.js runtime and npm packages in addition to Python dependencies
- **Build Step**: TypeScript compilation required before execution (adds build complexity)
- **Team Skills**: Developers must be proficient in both Python (watchers) and TypeScript (MCP server)
- **Deployment Complexity**: Must manage both Python virtual environment and Node.js node_modules
- **Debugging**: Cross-language debugging between Python watchers and TypeScript MCP server

## Alternatives Considered

### Alternative 1: FastMCP (Python)
- **Description**: Python-based MCP SDK with decorator-based API (@mcp.tool())
- **Pros**: Consistent with Bronze tier Python stack, no additional runtime, familiar to Python developers
- **Cons**: PROJECT_REFRENCE.md specifies Node.js v24+ as prerequisite (indicates TypeScript SDK is intended), less official support than TypeScript SDK
- **Why Rejected**: PROJECT_REFRENCE.md architecture requirements explicitly list Node.js v24+ as a prerequisite, indicating the official TypeScript MCP SDK is the intended framework. User identified this during task generation and requested Context7 research to validate proper implementation approach.

### Alternative 2: Custom MCP Implementation
- **Description**: Build custom MCP protocol implementation in Python
- **Pros**: Full control, Python-only stack, no external SDK dependencies
- **Cons**: Reinventing wheel, maintenance burden, protocol compliance risk, no official support
- **Why Rejected**: Violates "don't reinvent the wheel" principle. Official SDKs provide tested, maintained implementations with protocol guarantees.

### Alternative 3: Direct Gmail API Calls (No MCP)
- **Description**: Call Gmail API directly from Python watchers without MCP abstraction
- **Pros**: Simpler architecture, no MCP server needed, Python-only stack
- **Cons**: Violates MCP Server Architecture principle from constitution, loses Claude Code integration benefits, no standardized tool interface
- **Why Rejected**: Violates constitution principle requiring MCP server architecture for external actions. MCP provides standardized interface for Claude Code integration.

## References

- Feature Spec: [specs/002-silver-tier/spec.md](../../specs/002-silver-tier/spec.md)
- Implementation Plan: [specs/002-silver-tier/plan.md](../../specs/002-silver-tier/plan.md)
- Research Document: [specs/002-silver-tier/research.md](../../specs/002-silver-tier/research.md) (Section 3: MCP Server Framework)
- MCP API Contract: [specs/002-silver-tier/contracts/email-mcp-api.yaml](../../specs/002-silver-tier/contracts/email-mcp-api.yaml)
- Related ADRs: None (first ADR for Silver tier)
- Evaluator Evidence: [history/prompts/002-silver-tier/0003-silver-tier-task-generation.tasks.prompt.md](../prompts/002-silver-tier/0003-silver-tier-task-generation.tasks.prompt.md) (Documents correction from FastMCP to TypeScript SDK based on PROJECT_REFRENCE.md)
