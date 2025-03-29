import pprint
import json5
import matlab.engine
import matplotlib.pyplot as plt
import inspect
import pandas as pd
import json
import numpy as np
import re
from qwen_agent.agents import Agent
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.llm.schema import Message

# 注册MATLAB绘图工具（替换原my_image_gen）
@register_tool('matlab_plotter')
class MATLABPlotter(BaseTool):
    description = '调用MATLAB进行科学绘图，支持2D/3D图表生成与动态更新'
    parameters = [
        {
            'name': 'command',
            'type': 'string',
            'description': 'MATLAB绘图指令，例如："plot(sin(0:0.1:10))"',
            'required': True
        },
        {
            'name': 'data_source',
            'type': 'string',
            'description': '数据来源，可选值为 "local_variable" 或 "csv_file"',
            'required': False
        },
        {
            'name': 'variable_name',
            'type': 'string',
            'description': '当 data_source 为 "local_variable" 时，指定 Python 中的变量名',
            'required': False
        },
        {
            'name': 'csv_file_path',
            'type': 'string',
            'description': '当 data_source 为 "csv_file" 时，指定 CSV 文件的路径',
            'required': False
        }
    ]

    def __init__(self, cfg=None):
        super().__init__(cfg)
        # 启动MATLAB引擎（保持长连接）
        self.eng = matlab.engine.start_matlab()
        self.fig = None  # 用于保存当前图形句柄

    def call(self, params: str, **kwargs) -> str:
        params = json5.loads(params)
        command = params['command']
        data_source = params.get('data_source', None)
        matlab_code = []

        try:
            if data_source == 'local_variable':
                variable_name = params['variable_name']
                # 获取本地变量的值
                local_variable = kwargs.get(variable_name)
                if local_variable is None:
                    return f"Error: Local variable {variable_name} not found."
                # 将 Python 变量转换为 MATLAB 变量
                if isinstance(local_variable, np.ndarray):
                    matlab_variable = matlab.double(local_variable.tolist())
                elif isinstance(local_variable, (int, float)):
                    matlab_variable = matlab.double([local_variable])
                elif isinstance(local_variable, list):
                    matlab_variable = matlab.double(local_variable)
                else:
                    return f"Error: Unsupported variable type for {variable_name}"
                self.eng.workspace[variable_name] = matlab_variable
                matlab_code.append(f"{variable_name} = {matlab_variable};")
            elif data_source == 'csv_file':
                csv_file_path = params['csv_file_path']
                try:
                    # 判断文件格式
                    file_extension = csv_file_path.split('.')[-1].lower()
                    if file_extension == 'csv':
                        df = pd.read_csv(csv_file_path)
                    elif file_extension == 'xlsx' or file_extension == 'xls':
                        df = pd.read_excel(csv_file_path)
                    elif file_extension == 'json':
                        with open(csv_file_path, 'r') as f:
                            data = json.load(f)
                        df = pd.DataFrame(data)
                    elif file_extension == 'txt':
                        df = pd.read_csv(csv_file_path, sep='\t')  # 假设 txt 文件以制表符分隔
                    else:
                        return f"Error: Unsupported file format: {file_extension}"

                    # 将数据转换为 MATLAB 矩阵
                    matlab_data = matlab.double(df.values.tolist())
                    self.eng.workspace['csv_data'] = matlab_data
                    matlab_code.append(f"csv_data = {matlab_data};")
                except FileNotFoundError:
                    return f"Error: File {csv_file_path} not found."
                except Exception as e:
                    return f"Error reading file: {str(e)}"

            print("###1")
            # 执行MATLAB命令
            if not self.fig:
                self.fig = self.eng.figure(nargout=1)
            self.eng.eval(command, nargout=0)
            matlab_code.append(f"figure({self.fig});")
            matlab_code.append(command)

            # 保存图像到临时文件
            self.eng.saveas(self.fig, 'temp_plot.png', nargout=0)
            matlab_code.append("saveas(gcf, 'temp_plot.png');")

            # 保存MATLAB代码到txt文件
            with open('matlab_code.txt', 'w') as f:
                f.write('\n'.join(matlab_code))

            # 在Python中直接显示图像
            img = plt.imread('temp_plot.png')
            plt.imshow(img)
            plt.axis('off')
            plt.show()

            return json5.dumps(
                {'image_url': 'file://temp_plot.png'},
                ensure_ascii=False
            )
        except Exception as e:
            # 打印详细的错误信息
            import traceback
            traceback.print_exc()
            return f"MATLAB Error: {str(e)}"

    def __del__(self):
        # 关闭MATLAB引擎
        if hasattr(self, 'eng'):
            self.eng.quit()

class MATLABPlottingAgent(Agent):
    def __init__(self, llm_cfg, system_message, function_list, files):
        super().__init__(function_list=function_list, llm=llm_cfg, system_message=system_message)
        self.files = files
        self.matlab_plotter = MATLABPlotter()

    def _run(self, messages, **kwargs):
        # 获取当前作用域内的所有本地变量
        filtered_vars = {k: v for k, v in kwargs.items() if isinstance(v, (int, float, list, np.ndarray))}
        filtered_vars.pop('messages', None)

        for response in self._call_llm(messages=messages):
            response = response[0]
            if response.function_call:
                tool_name = response.function_call.name
                params = response.function_call.parameters
                params_str = json5.dumps(params)
                result = self.matlab_plotter.call(params_str, **filtered_vars)
                try:
                    result_dict = json5.loads(result)
                    if 'image_url' in result_dict:
                        print(f"Generated image: {result_dict['image_url']}")
                    yield [Message(role='assistant', content=result)]
                except json5.JSONDecodeError:
                    yield [Message(role='assistant', content=f"Error: {result}")]
            else:
                yield [Message(role='assistant', content=response.content)]

# 配置LLM（保持原配置）
llm_cfg = {
    'model': 'qwen-max',
    'model_server': 'dashscope',
    'api_key': 'sk-b4346fdeefa94b6392bd0c2c50bff7f2',
    'generate_cfg': {'top_p': 0.8}
}

# 更新系统指令
system_instruction = '''你是一个科学计算助手，请按以下步骤响应用户：
1. 解析用户的绘图需求，生成MATLAB绘图指令
2. 调用matlab_plotter工具生成初始图表
3. 根据用户调整需求，生成新的MATLAB命令更新图表
4. 使用plt.show()展示最终图像'''

# 工具列表修改
tools = ['matlab_plotter', 'code_interpreter']  # 移除非必要的图像生成工具
files = ['./examples/resource/matlab_doc.docx']  # 提供MATLAB绘图文档

# 初始化助手
bot = MATLABPlottingAgent(llm_cfg=llm_cfg,
                          system_message=system_instruction,
                          function_list=tools,
                          files=files)

x = np.linspace(0, 10, 100)
y = np.sin(x)
print(x)
print(y)

# 交互循环示例
messages = []
try:
    while True:
        query = input("User: ").strip()
        if not query:
            break
        messages.append(Message(role='user', content=query))

        for response in bot._run(messages=messages, x=x, y=y):
            pass
            #print(response[0].content)
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    # 确保在程序结束时关闭MATLAB引擎
    if hasattr(bot, 'matlab_plotter'):
        del bot.matlab_plotter