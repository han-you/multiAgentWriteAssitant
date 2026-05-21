from typing import TypedDict
class ReportState(TypedDict):
    topic:str
    target_word_count:int
    draft:str
    search_results:str
    editor_feedsback:str
    editor_comment:str          #用于editor节点反馈信息
    reversion_count:int         #editor循环执行次数