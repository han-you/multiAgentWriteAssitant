from langgraph.graph import StateGraph,START,END
from state import ReportState
from nodes import writer_node,research_node

builder=StateGraph(ReportState)

builder.add_node("researcher",research_node)
builder.add_node("writer",writer_node)
builder.add_edge(START,"researcher")
builder.add_edge("researcher","writer")
builder.add_edge("writer",END)

graph=builder.compile()
result=graph.invoke({
    "topic": "中国新能源汽车出海市场现状",
    "target_word_count": 600,
    "draft": ""
})
with open("./result_add_searcher.md","w",encoding="utf-8") as fp:
    fp.write(result["draft"])