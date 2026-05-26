from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()
api_key=os.getenv("DEEPSEEK_API_KEY")
base_url=os.getenv("DEEPSEEK_BASE_URL")
client=OpenAI(api_key=api_key,base_url=base_url)

def callLLM(prompt:str,temperature=1)->str:
    response=client.chat.completions.create(
        model="deepseek-v4-flash",
        temperature=temperature,
        messages=[
            {"role": "user","content": prompt}
        ]
    )
    # print("llm返回结果为:"+str(response))
    return {"content":response.choices[0].message.content,
            "completion_tokens":response.usage.completion_tokens,
            "prompt_tokens":response.usage.prompt_tokens
            }

