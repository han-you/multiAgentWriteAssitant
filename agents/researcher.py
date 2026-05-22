from llm import callLLM
from ddgs import DDGS
from state import ReportState
from utils import clean_json_from_markdown
import json


CLEANING_PROMPT = """你是一个信息清洗专家。你的任务是从以下检索结果中去除噪声，只保留与用户问题相关的实质性内容，并返回结构化的JSON数据。
        ## 用户问题
        {topic}

        ## 原始检索结果
        {retrived_search}

        ## 去噪规则

        ### 需要保留的内容：
        - 直接回答用户问题的句子或段落
        - 包含关键事实、数据、定义、步骤、原因、示例的内容
        - 能够补充或解释用户所需信息的上下文

        ### 需要去除的噪声：
        - 纯粹的导航、菜单、面包屑导航文字（如"首页 > 产品 > 详情"）
        - 广告、推广、推荐阅读、相关文章（除非与问题强相关）
        - 版权声明、备案号、联系方式、公司介绍（不提供问题答案的部分）
        - 重复出现且无信息量的句子（如"点击这里了解更多"）
        - 与用户问题完全无关的正文片段
        - 明显来自网站模板的固定文字（如"发表评论""分享到微信"）

        ## 输出格式要求

        必须返回一个严格的JSON数组，每个元素包含以下三个字段：

        ```json
        [
        {{
            "title": "原始标题",
            "url": "原始链接",
            "cleaned_body": "清洗后的正文内容"
        }}
        ]"""


def research_node(state:ReportState)->dict:
    print("来到researcher")
    text="【搜索结果摘要】\n"
    try:
        search_topic=""
        if state["reversion_count"]>0:
            search_topic=f"{state['topic']} (优化方向: {state['search_comment']})"
        else:
            search_topic=state["topic"]
        results=DDGS().text(search_topic,max_results=5,backend="lite")

        # # 方法一 body长度小于20
        # count=1
        # for result in results:
        #     if len(result["body"])>=20:
        #         text+=str(count)+'.['+result["title"]+']('+result["href"]+'):'+result["body"]+'\n'
        #         count+=1

        #方法二 使用LLM整理
        print("start search")
        retrived_search=""
        count=1
        for result in results:
            retrived_search+=str(count)+'.['+result["title"]+']('+result["href"]+'):'+result["body"]+'\n'
            count+=1
        # print("整理原始检索结果: "+retrived_search)
        prompt=CLEANING_PROMPT.format(topic=state["topic"],retrived_search=retrived_search)
        # print("prompt 预览:"+CLEANING_PROMPT[:200])
        # print("start_clean")
        cleaned_research=callLLM(prompt)
        # print("LLM 原始响应:"+cleaned_research)
        #json对LLM清洗结果解析
        data_list=json.loads(clean_json_from_markdown(cleaned_research))
        count=1
        for result in data_list:
            text+=str(count)+'.['+result["title"]+']('+result["url"]+'):'+result["cleaned_body"]+'\n'
            count+=1
    
        #保存搜索结果
        with open("./research_result.txt","w",encoding="utf-8") as fp:
            fp.write(text)
        


    except Exception as e:
        text=f"【搜索失败】{str(e)}。请基于已有知识推断，并注明数据来源局限。"
    return {"search_results": text}
