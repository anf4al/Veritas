import hashlib
import json
from typing import Set, Tuple

class AgentSafeguardError(Exception):
    pass

class AgentBudgetTracker:
    def __init__(self, max_tool_calls: int = 10, max_steps: int = 8):
        self.max_tool_calls = max_tool_calls
        self.max_steps = max_steps
        self.tool_calls_count = 0
        self.steps_count = 0
        self._seen_calls: Set[str] = set()

    def record_step(self):
        self.steps_count += 1
        if self.steps_count > self.max_steps:
            raise AgentSafeguardError(
                f"Agent step limit exceeded (maximum {self.max_steps} steps). Terminating workflow."
            )

    def record_tool_call(self, tool_name: str, args: dict):
        self.tool_calls_count += 1
        if self.tool_calls_count > self.max_tool_calls:
            raise AgentSafeguardError(
                f"Agent tool budget exceeded (maximum {self.max_tool_calls} calls). Terminating workflow."
            )

        # Hash call name + arguments to detect loop / repeated call
        call_repr = f"{tool_name}:{json.dumps(args, sort_keys=True)}"
        call_hash = hashlib.sha256(call_repr.encode("utf-8")).hexdigest()
        if call_hash in self._seen_calls:
            raise AgentSafeguardError(
                f"Repeated identical tool call detected for '{tool_name}' with arguments {args}. Terminating loop."
            )
        self._seen_calls.add(call_hash)
