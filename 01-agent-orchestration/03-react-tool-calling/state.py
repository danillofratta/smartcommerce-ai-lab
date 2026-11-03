from langgraph.graph import MessagesState


class State(MessagesState):
    """Shared message history, accumulated with the inherited add_messages reducer."""
