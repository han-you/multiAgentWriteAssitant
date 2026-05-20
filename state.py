from typing import TypedDict
class ReportState(TypedDict):
    topic:str
    target_word_count:int
    draft:str
    search_results:str