import requests

# 已知的大模型的URL
model_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"  # 替换为实际URL
# 秘钥
api_key = "5cdc185a9184982308710749d57dc3eb.OCHF8wVVAo9LggPX"  # 替换为实际秘钥

# 设置请求头
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 定义输入数据
input_data = {
    "model": "glm-4-plus",  # 确保这是正确的模型名称
    "messages": [
        {"role": "user", "content": "绘制sin图,给出五个点的数据"}  # 示例用户消息
    ],
    "temperature": 0.7,  # 可选参数
}

# 发送POST请求到模型
try:
    response = requests.post(model_url, headers=headers, json=input_data)

    # 检查请求状态
    if response.status_code == 200:
        result = response.json()
        print("Model Response:", result)
    else:
        print("Error:", response.status_code, response.text)
except Exception as e:
    print("An error occurred:", str(e))
