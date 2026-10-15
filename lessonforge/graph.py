from langgraph.graph import StateGraph, START, END
from .nodes import LessonState, generate_lesson, evaluate_lesson, route_after_evaluation, mark_approved, mark_rejected

def build_graph():
    graph = StateGraph(LessonState)
    graph.add_node("generate", generate_lesson)
    graph.add_node("evaluate", evaluate_lesson)
    graph.add_node("approve", mark_approved)
    graph.add_node("reject", mark_rejected)

    graph.add_edge(START, "generate")
    graph.add_edge("generate", "evaluate")
    graph.add_conditional_edges("evaluate", route_after_evaluation, {
        "approve": "approve",
        "retry": "generate",
        "reject": "reject",
    })
    graph.add_edge("approve", END)
    graph.add_edge("reject", END)
    return graph.compile()
