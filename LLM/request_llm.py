# 请先安装 OpenAI SDK: `pip3 install openai`

from openai import OpenAI


def request_llm(prompt: str, api_key: str = None) -> str:
    """
    请求 LLM 接口，获取模型的回复。

    :param prompt: 用户输入的提示语
    :param api_key: OpenAI API 密钥
    :return: 模型的回复内容或错误信息
    """
    if api_key is None:
        api_key = "sk-2c55102070a54aa0acf8c21766719e45"
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        # 错误码及解决方法提示
        error_map = {
            400: "格式错误：请根据错误信息提示修改请求体。",
            401: "认证失败：请检查您的 API key 是否正确。",
            402: "余额不足：请确认账户余额，并充值。",
            422: "参数错误：请根据错误信息提示修改相关参数。",
            429: "请求速率达到上限：请合理规划您的请求速率。",
            500: "服务器故障：请等待后重试。",
            503: "服务器繁忙：请稍后重试您的请求。",
        }
        # 获取错误码
        code = getattr(e, "status_code", None)
        if code in error_map:
            return f"错误码 {code}：{error_map[code]}"
        return f"调用失败，错误信息：{str(e)}"
