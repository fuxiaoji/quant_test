import request_llm
while True:
    user_input = input("请输入提示语：")
    if user_input.lower() == "exit":
        break
    response = request_llm.request_llm(user_input)
    print(f"模型回复：{response}")