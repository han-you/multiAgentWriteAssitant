from typing import TypedDict
class ReportState(TypedDict):
    topic:str
    target_word_count:int
    draft:str
    search_results:str
    editor_action:str
    search_comment:str          #editor反馈给researcher节点反馈信息
    write_comment:str          #editor反馈给writer节点的信息  
    reversion_count:int         #editor循环执行次数
    tokens:list                 #查看消耗的tokens
