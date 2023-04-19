import userconfig
import openai
import os

def gpt_stream(username,question):
    """
    实现gpt请求和流式输出
    :param username: 用户名
    :param question: 问题内容
    :return: 调用gpt流式输出的结果
    """
    try:
        userconfig.check_quota(username)
    except Exception as e:
        yield "data: %s\n\n" % str(e)
        yield "data: [DONE]\n\n"
        return
    openai.api_key = os.getenv("OPENAI_API_KEY")

    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=[
            {"role": "user", "content": question}
        ],
        stream=True,
        user=username
    )
    for chunk in result:
        if chunk["choices"][0]["finish_reason"] is not None:
            data = "[DONE]"
        else:
            data = chunk["choices"][0]["delta"].get("content", "")
        yield "data: %s\n\n" % data.replace("\n", "<br />")