from langgraph.graph import StateGraph,START,END
from state import ReportState
from nodes import writer_node,research_node,editor_node

builder=StateGraph(ReportState)

builder.add_node("researcher",research_node)
builder.add_node("writer",writer_node)
builder.add_node("editor",editor_node)

def editor_router(state:ReportState):
    if state["reversion_count"]>=5 or state["editor_feedsback"]=="通过":
        return "end"
    else:
        return "writer"

builder.add_edge(START,"researcher")
builder.add_edge("researcher","writer")
builder.add_edge("writer","editor")
builder.add_conditional_edges("editor",editor_router,{
    "writer":"writer",
    "end":END
})

graph=builder.compile()
result=graph.invoke({
    "topic": "中国新能源汽车出海市场现状",
    "target_word_count": 600,
    "draft": "",
    "search_results":"",
    "editor_feedsback":"",
    "editor_comment":"",
    "reversion_count":0
})
with open("./result_add_searcher.md","w",encoding="utf-8") as fp:
    fp.write(result["draft"])