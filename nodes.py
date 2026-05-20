from state import ReportState
from openai import OpenAI
from ddgs import DDGS
api_key="sk-31bc0ec66c3b459d9be663e7eff40384"
base_url="https://api.deepseek.com"
client=OpenAI(api_key=api_key,base_url=base_url)

def writer_node(state: ReportState)->dict:

    prompt="""你是一名资深行业研究员、战略咨询顾问和商业分析师。请围绕以下主题撰写
    一份专业、结构清晰、逻辑严谨的行业分析报告。"""+"【参考信息】"+state["search_results"]+"\n【分析主题】"+state["topic"]+"【最大字数】不超过{"+str(state["target_word_count"])+"""} 字。
            【报告要求】
            1. 报告应面向企业管理层、投资人或战略决策者，语言专业但易读。
            2. 请基于可验证的信息、行业逻辑和商业分析框架进行分析。
            3. 如果涉及市场规模、增长率、政策、技术趋势、竞争格局等数据，请尽量说明数据来源或判断依据。
            4. 如无法获取最新数据，请明确说明，并基于已有信息进行合理推断，避免编造。
            5. 内容应有观点、有判断，不要只做信息堆砌。
            6. 控制在字数限制内，避免冗长铺陈。

            【建议结构】
            一、行业概况
            - 行业定义与产业边界
            - 核心产品、服务或商业模式
            - 行业所处发展阶段

            二、市场规模与增长趋势
            - 当前市场规模或需求水平
            - 近年增长趋势
            - 未来增长驱动因素与制约因素

            三、产业链分析
            - 上游：关键资源、原材料、技术或供应商
            - 中游：主要生产、服务或平台环节
            - 下游：客户群体、应用场景与需求变化
            - 产业链利润分布与关键控制点

            四、竞争格局
            - 主要参与者类型
            - 头部企业或代表性企业
            - 行业集中度与竞争壁垒
            - 主要竞争策略

            五、政策、技术与宏观环境
            - 政策监管影响
            - 技术发展趋势
            - 宏观经济、人口、消费或资本环境影响

            六、商业机会与风险
            - 主要增长机会
            - 潜在进入机会
            - 核心风险，包括政策风险、技术风险、市场风险、竞争风险等

            七、未来趋势判断
            - 未来 3-5 年行业发展方向
            - 可能出现的结构性变化
            - 对企业、投资人或创业者的建议

            【输出格式】
            请使用中文输出。
            使用清晰标题和分段。
            重点内容可用项目符号呈现。
            结尾请给出 3-5 条简明的战略建议。"""
    
    response=client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "user","content": prompt}
        ]
    )
    draft=response.choices[0].message.content
    return {"draft":draft}


def research_node(state:ReportState)->dict:
    text="【搜索结果摘要】\n"
    try:
        results=DDGS().text(state["topic"],max_results=5,backend="lite")
        #方法一 body长度小于20
        count=1
        for result in results:
            if len(result["body"])>=20:
                text+=str(count)+'.['+result["title"]+']('+result["href"]+'):'+result["body"]+'\n'
                count+=1
        with open("./research_result.txt","w",encoding="utf-8") as fp:
            fp.write(text)
        #方法二 使用LLM整理
    except Exception as e:
        text=f"【搜索失败】{str(e)}。请基于已有知识推断，并注明数据来源局限。"
    return {"search_results": text}
    

    
    



