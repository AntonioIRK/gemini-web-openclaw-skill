from openclaw_gemini_web.models import WorkflowState
from openclaw_gemini_web.web.state_machine import GeminiWebStateMachine, StorybookStateMachine


def test_state_machine_advances():
    machine = GeminiWebStateMachine()
    assert machine.current == WorkflowState.INIT
    machine.advance(WorkflowState.OPENING_GEMINI)
    assert machine.current == WorkflowState.OPENING_GEMINI


def test_storybook_state_machine_alias_advances():
    machine = StorybookStateMachine()
    assert machine.current == WorkflowState.INIT
    machine.advance(WorkflowState.OPENING_GEMINI)
    assert machine.current == WorkflowState.OPENING_GEMINI
