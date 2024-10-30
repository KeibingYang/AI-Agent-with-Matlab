from flask import Flask, request, jsonify
import openai
import matlab.engine

app = Flask(__name__)

# 初始化 MATLAB 引擎
matlab_eng = matlab.engine.start_matlab()


model_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"  # 替换为实际URL
# OpenAI API 密钥
api_key = '5cdc185a9184982308710749d57dc3eb.OCHF8wVVAo9LggPX'

@app.route('/api/generate', methods=['POST'])
def generate():
    user_input = request.json.get('input')

    # 调用大模型生成文本
    response = requests.post(model_url, headers=headers, json=input_data)
    
    generated_text = response.choices[0].message.content
    
    # 使用 MATLAB 生成图片
    # 假设使用 MATLAB 函数 generate_image，该函数返回图片文件路径
    image_path = matlab_eng.generate_image(generated_text)

    # 返回图片 URL
    return jsonify({'image_url': image_path})

if __name__ == '__main__':
    app.run(debug=True)
