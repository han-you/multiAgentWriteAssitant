from langgraph.graph import StateGraph,START,END
from state import ReportState
from agents import *
from langgraph.checkpoint.postgres import PostgresSaver
from dotenv import load_dotenv
import os
import json
load_dotenv()
username=os.getenv("DATABASE_USERNAME")
server_ip=os.getenv("SERVER_IP")
port=os.getenv("DATABASE_PORT")
passwd=os.getenv("DATABASE_PASSWORD")

DB_URI = "postgresql://{username}:{passwd}@{IP}:{port}/agents".format(
    username=username,
    passwd=passwd,
    IP=server_ip,
    port=port
)




builder=StateGraph(ReportState)

builder.add_node("researcher",research_node)
builder.add_node("writer",writer_node)
builder.add_node("editor",editor_node)

def editor_router(state:ReportState):
    if state["reversion_count"]>=5:
        return "end"
    else:
        return state["editor_action"]

builder.add_edge(START,"researcher")
builder.add_edge("researcher","writer")
builder.add_edge("writer","editor")
builder.add_conditional_edges("editor",editor_router,{
    "writer":"writer",
    "end":END,
    "researcher":"researcher"
})
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()
    graph=builder.compile(checkpointer=checkpointer)
    config={"configurable":{"thread_id":"report_008"}}
    existing=graph.get_state(config)
    if not existing.values:
        print("首次运行")
        result=graph.invoke({
            "topic": "中国新能源汽车出海市场现状",
            "target_word_count": 600,
            "draft": "",
            "search_results":"",
            "editor_action":"",
            "search_comment":"",
            "write_comment":"",
            "reversion_count":0,
            "tokens":[]
        },
        config=config)
    else:
        print(f"恢复运行，上次状态: {existing}")
        result = graph.invoke(None, config=config)
    thread_id=config["configurable"]["thread_id"]

    with open(f"./result_{thread_id}.md","w",encoding="utf-8") as fp:
        fp.write(result["draft"])
    with open(f"./token_usag_{thread_id}.md","w",encoding="utf-8") as fp:
        for item in result["tokens"]:
            fp.write(json.dumps(item, ensure_ascii=False) + "\n")
        
