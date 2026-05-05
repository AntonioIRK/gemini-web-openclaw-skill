from __future__ import annotations

from dataclasses import dataclass, field

from ..models import WorkflowState


@dataclass
class GeminiWebStateMachine:
    history: list[WorkflowState] = field(default_factory=lambda: [WorkflowState.INIT])

    @property
    def current(self) -> WorkflowState:
        return self.history[-1]

    def advance(self, state: WorkflowState) -> WorkflowState:
        self.history.append(state)
        return state


StorybookStateMachine = GeminiWebStateMachine
