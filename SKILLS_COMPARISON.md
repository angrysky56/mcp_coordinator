# Skills System Comparison

This document compares the skills implementation in `mcp-coordinator` (enhanced) with the reference implementation in `mcp-code-execution-enhanced`.

## 1. mcp-code-execution-enhanced (Reference)

### Architecture
- **Storage**: File-based. Skills are Python scripts located in a `skills/` directory.
- **Execution**: CLI-based. A `harness.py` script loads and executes the skill script.
- **Discovery**: File system scanning.

### Pros
- **Simplicity**: Easy to understand. Just Python files.
- **Version Control**: Skills are directly versioned with the codebase (Git).
- **Editability**: Easy to edit with any text editor or IDE.

### Cons
- **Metadata Management**: Difficult to store and query structured metadata (tags, descriptions, usage counts) without parsing files.
- **Search**: Relies on text search or file naming conventions.
- **Dynamic Updates**: Updating a skill requires file system access, which might be restricted in some environments.

## 2. mcp-coordinator (Enhanced)

### Architecture
- **Storage**: Hybrid.
    - **Primary**: SQLite Database (`skills.db`) stores code, name, description, tags, and version history.
    - **Fallback**: File-based (`skills/` directory) for manually added or version-controlled skills.
- **Execution**: `run_skill` tool wraps a `skill_harness.py`.
    - Supports executing skills from **both** the database and the file system.
    - Uses `subprocess` for isolation (can be extended to Docker/E2B).
- **Management**: Dedicated MCP tools (`save_skill`, `get_skill`, `list_skills`, `search_skills`, `delete_skill`).

### Key Enhancements
1.  **Robust Client Management**:
    -   Refactored `McpClientManager` uses a state machine and manual context management to prevent `RuntimeError` during cleanup (addressing `anyio` cancel scope issues).
    -   Lazy loading ensures connections are only established when needed.

2.  **Unified Execution Model**:
    -   The `skill_harness.py` provides a unified entry point for both DB-backed and file-backed skills.
    -   It handles argument parsing (JSON and key-value) and error reporting consistently.

3.  **Best of Both Worlds**:
    -   **Database**: Enables dynamic skill creation by agents (`save_skill`), rich searching, and metadata management.
    -   **File Fallback**: Allows developers to check in core skills (like `research.py`) to Git and have them immediately available without DB population.

### Conclusion
The `mcp-coordinator` implementation builds upon the `mcp-code-execution-enhanced` pattern by adding a database layer for better agentic interaction (dynamic learning) while preserving the simplicity and developer experience of file-based skills. The refactored client manager ensures stability and reliability for long-running agent sessions.
