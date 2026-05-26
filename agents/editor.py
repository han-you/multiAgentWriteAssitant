from llm import callLLM
from utils import clean_json_from_markdown
from state import ReportState
import json

EDITOR_PROMPT = """
    你是一名严苛的行业报告编辑。请对以下生成的报告进行严格审核，并返回结构化的JSON结果。

    ## 审核要求

    ### 1. 原始要求
    - **报告主题**：{topic}
    - **目标字数**：{target_word_count} 字
    - **允许偏差**：±20%（即 {min_words} - {max_words} 字）

    ### 2. 审核维度

    #### 2.1 字数审核
    - 计算报告实际字数（中文字符数）
    - 判断是否在允许范围内
    - 如超出范围，说明超出多少或不足多少

    #### 2.2 结构审核
    检查是否包含以下七个章节：
    - 一、行业概况
    - 二、市场规模与增长趋势
    - 三、产业链分析
    - 四、竞争格局
    - 五、政策、技术与宏观环境
    - 六、商业机会与风险
    - 七、未来趋势判断

    #### 2.3 事实一致性审核
    检查是否存在以下矛盾：
    - 同一数据前后不一致
    - 逻辑矛盾
    - 时间线矛盾
    - 因果关系混乱

    #### 2.4 语言质量审核
    - 是否专业、流畅、无语法错误
    - 是否有明显的数据编造
    - 是否有冗余重复内容
    - 是否有口语化表达

    ### 3. 审核标准
    - **通过**：所有维度基本合格，仅有个别小问题
    - **重写**：存在重大问题，需要 Writer 重写
    - **资料不足**：缺少关键信息，需要 Researcher 补充资料

    ### 4. 行动决策规则

    根据审核结果，决定下一步行动：

    | 情况 | action | write_comment | search_comment |
    |------|--------|----------------|----------------|
    | 报告质量合格，无需修改 | `"end"` | 总结评价，可给出优化建议 | `""` (空字符串) |
    | 报告有问题，但资料充足，只需重写 | `"writer"` | 详细说明需要修改的问题 | `""` (空字符串) |
    | 缺少关键信息，需要补充资料 | `"researcher"` | 说明当前报告的问题 | 详细列出需要搜索什么资料 |

    ### 5. 需要补充资料的判断标准

    以下情况应设置 action 为 "researcher"：
    - 缺少市场规模、增长率等关键数据
    - 缺少政策、法规相关信息
    - 缺少主要竞争对手信息
    - 缺少技术发展趋势信息
    - 参考信息不足以支撑完整报告
    - 报告中的数据来源不明确或缺失

    ## 待审核报告
    {draft}

    ## 输出格式

    必须返回严格的JSON数组，格式如下：

    ```json
    [
    {{
        "action": "writer/researcher/end",
        "write_comment": "对Writer生成内容的审核意见（每次必填）",
        "search_comment": "需要补充什么资料（仅当action为researcher时填写，否则为空字符串）"
    }}
    ]"""


def editor_node(state:ReportState)->dict:
    print("start editor")
    count=state.get("reversion_count",0)
    draft=state["draft"]
    topic=state["topic"]
    target_word_count=state["target_word_count"]
    min_words=int(target_word_count*0.8)
    max_words=int(target_word_count*1.2)
    prompt=EDITOR_PROMPT.format(
        topic=topic,
        target_word_count=target_word_count,
        min_words=min_words,
        max_words=max_words,
        draft=draft
    )
    response=callLLM(prompt,0.2)
    # print("raw editor message"+str(editor_message))
    # print("===== 实际收到的内容 =====")
    # print(repr(editor_message))
    editor_message=response["content"]
    print(editor_message)
    #json对editor结果解析
    data_list=json.loads(clean_json_from_markdown(editor_message))
    action=data_list[0]["action"]
    search_comment=data_list[0]["search_comment"]
    write_comment=data_list[0]["write_comment"]
    # print("result:"+result)
    # print("comment:"+comment)
    # sys.exit()
    with open("./editor_comment-"+str(state["reversion_count"]),"w",encoding="utf-8") as fp:
        fp.write("search_comment:"+search_comment+'\n')
        fp.write("write_comment:"+write_comment)
    tokens_list=state["tokens"]
    tokens_list.append({"role":"editor","completion_tokens":response["completion_tokens"],"prompt_tokens":response["prompt_tokens"]})
    print("end editor")
    return {"tokens":tokens_list,"editor_action":action,"search_comment":search_comment,"write_comment":write_comment,"reversion_count":count+1}