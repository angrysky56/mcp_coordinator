"""
Enhanced executor using smolagents with multiple backend support.

Supports:
- Local execution (LocalPythonExecutor) - default
- Docker execution (best security/performance balance)
- E2B remote execution (cloud-based)
- Modal serverless execution
- WASM execution (Pyodide/Deno)
"""

from pathlib import Path
from typing import Any, Literal

from mcp_coordinator.config import ConfigManager

try:
    from smolagents import CodeAgent, LiteLLMModel, LocalPythonExecutor
except ImportError:
    raise ImportError("smolagents is required. Install with: uv pip install smolagents")


ExecutorType = Literal["local", "docker", "e2b", "modal", "wasm"]


class SmolExecutor:
    """
    Enhanced executor using smolagents with configurable backends.

    Provides multiple execution strategies:
    - local: LocalPythonExecutor (fast, basic security)
    - docker: Docker containers (best balance)
    - e2b: E2B cloud execution (managed service)
    - modal: Modal serverless (scalable)
    - wasm: WebAssembly (portable, isolated)
    """

    def __init__(
        self,
        executor_type: ExecutorType = "local",
        allowed_imports: list[str] | None = None,
        workspace_dir: Path | None = None,
        config_manager: ConfigManager | None = None,
    ) -> None:
        """
        Initialize smol executor with specified backend.

        Args:
            executor_type: Backend type to use
            allowed_imports: List of allowed imports for local executor
            workspace_dir: Working directory for file operations
            config_manager: Configuration manager instance
        """
        self.executor_type = executor_type
        self.workspace_dir = workspace_dir or Path("./workspace")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        self.config_manager = config_manager or ConfigManager()

        # Set up allowed imports for local executor
        self.allowed_imports = allowed_imports or [
            "mcp_tools",
            "skills",
            "numpy",
            "pandas",
            "json",
            "csv",
            "datetime",
            "math",
            "statistics",
            "collections",
            "itertools",
            "functools",
            "pathlib",
            "typing",
            "requests",
            "httpx",
        ]

        # Initialize executor based on type
        self._executor = self._create_executor()

    def _create_executor(self) -> Any:
        """Create the appropriate executor based on type."""
        if self.executor_type == "local":
            return LocalPythonExecutor(additional_authorized_imports=self.allowed_imports)

        elif self.executor_type == "docker":
            try:
                from smolagents import DockerExecutor

                docker_config = self.config_manager.get_docker_config()
                return DockerExecutor(
                    image=docker_config["image"],
                    mem_limit=docker_config["mem_limit"],
                    cpu_quota=docker_config["cpu_quota"],
                )
            except ImportError:
                raise ImportError("Docker support requires: uv pip install 'smolagents[docker]'")

        elif self.executor_type == "e2b":
            try:
                from smolagents import E2BExecutor

                return E2BExecutor()
            except ImportError:
                raise ImportError("E2B support requires: uv pip install 'smolagents[e2b]'")

        elif self.executor_type == "modal":
            try:
                from smolagents import ModalExecutor

                return ModalExecutor()
            except ImportError:
                raise ImportError("Modal support requires: uv pip install 'smolagents[modal]'")

        elif self.executor_type == "wasm":
            try:
                from smolagents import WasmExecutor

                return WasmExecutor()
            except ImportError:
                raise ImportError("WASM support requires Deno to be installed")

        else:
            raise ValueError(f"Unknown executor type: {self.executor_type}. Choose from: local, docker, e2b, modal, wasm")

    def execute(self, code: str) -> Any:
        """
        Execute code using the configured executor.

        Args:
            code: Python code to execute

        Returns:
            Execution result
        """
        return self._executor(code)

    def cleanup(self) -> None:
        """Clean up executor resources (e.g., Docker containers)."""
        if hasattr(self._executor, "cleanup"):
            self._executor.cleanup()


class AgentExecutor:
    """
    High-level agent executor that can use Ollama or cloud models.

    This wraps smolagents' CodeAgent with proper LLM configuration.
    """

    def __init__(
        self,
        executor_type: ExecutorType = "local",
        model_provider: str = "ollama",
        workspace_dir: Path | None = None,
        config_manager: ConfigManager | None = None,
    ) -> None:
        """
        Initialize agent executor.

        Args:
            executor_type: Execution backend
            model_provider: LLM provider ('ollama', 'openai', 'anthropic', etc.)
            workspace_dir: Working directory
            config_manager: Configuration manager
        """
        self.executor_type = executor_type
        self.model_provider = model_provider
        self.workspace_dir = workspace_dir or Path("./workspace")
        self.config_manager = config_manager or ConfigManager()

        # Create model
        self.model = self._create_model()

        # Create agent with executor
        self.agent = CodeAgent(
            model=self.model,
            tools=[],
            executor_type=executor_type if executor_type != "local" else None,
        )

    def _create_model(self) -> Any:
        """Create LLM model based on provider."""
        if self.model_provider == "ollama":
            ollama_config = self.config_manager.get_ollama_config()
            return LiteLLMModel(
                model_id=f"ollama_chat/{ollama_config['model_id']}",
                api_base=ollama_config["api_base"],
                api_key="ollama",  # Ollama doesn't need real key
            )

        else:
            # For other providers, use LiteLLM with provider prefix
            # e.g., "openai/gpt-4", "anthropic/claude-3-opus"
            return LiteLLMModel(model_id=self.model_provider)

    def run(self, prompt: str) -> str:
        """
        Run agent with given prompt.

        Args:
            prompt: User prompt/task

        Returns:
            Agent response
        """
        return self.agent.run(prompt)

    def cleanup(self) -> None:
        """Clean up agent resources."""
        if hasattr(self.agent, "cleanup"):
            self.agent.cleanup()


def create_executor(
    executor_type: ExecutorType | None = None,
    config_manager: ConfigManager | None = None,
) -> SmolExecutor:
    """
    Factory function to create an executor with configuration.

    Args:
        executor_type: Executor backend (None = use config)
        config_manager: Configuration manager

    Returns:
        Configured SmolExecutor instance
    """
    config_manager = config_manager or ConfigManager()

    if executor_type is None:
        executor_type = config_manager.get_executor_type()  # type: ignore

    return SmolExecutor(
        executor_type=executor_type,
        config_manager=config_manager,
    )
