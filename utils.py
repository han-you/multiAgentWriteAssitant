import re
def clean_json_from_markdown(text):
    """移除 ```json 和 ``` 标记"""
    text = text.strip()
    # 移除开头的 ```json 或 ``` (带或不带换行)
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    # 移除结尾的 ```
    text = re.sub(r'\n?```\s*$', '', text)
    return text