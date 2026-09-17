import pytest
from backend.app.agents.safeguards import AgentBudgetTracker, AgentSafeguardError

def test_agent_max_tool_calls_limit():
    tracker = AgentBudgetTracker(max_tool_calls=3, max_steps=10)
    tracker.record_tool_call("tool_a", {"q": 1})
    tracker.record_tool_call("tool_b", {"q": 2})
    tracker.record_tool_call("tool_c", {"q": 3})

    with pytest.raises(AgentSafeguardError) as exc_info:
        tracker.record_tool_call("tool_d", {"q": 4})
    assert "budget exceeded" in str(exc_info.value)

def test_agent_loop_detection_repeated_calls():
    tracker = AgentBudgetTracker(max_tool_calls=10, max_steps=10)
    tracker.record_tool_call("search_enterprise_knowledge", {"query": "leave policy"})

    with pytest.raises(AgentSafeguardError) as exc_info:
        tracker.record_tool_call("search_enterprise_knowledge", {"query": "leave policy"})
    assert "Repeated identical tool call detected" in str(exc_info.value)

