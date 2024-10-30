clc
clear
close all
%%
% 假设你的Python脚本文件名为 chat_model.py
% Question=" "
[status, cmdout] = system('python ZhipuAI.py 2>&1');

if status == 0
    disp('Python script executed successfully:');
    disp(cmdout);
else
    disp('Error executing Python script:');
    disp(cmdout);
end

%%
string_cmdout = string(cmdout);

% 然后使用上述提取代码...


% 使用正则表达式提取 content
%pattern = '''content'': ''(.*?)''\s*,\s*''role'':';
%pattern = '''content'' ''(.*?)''\}}'; % 匹配 content 中的内容
pattern = '"(.*?)"';  % 匹配双引号之间的内容
matches = regexp(string_cmdout, pattern, 'tokens');

display(matches);

% 检查是否找到了匹配
if ~isempty(matches)
    % 提取第一组匹配的内容（旅游计划）
    code = matches{1}{1}; % matches{1}{1} 获取第一个匹配项
    % 替换\n为换行符
    code = strrep(code, '\n', newline);
    disp('成功提取信息:');
    disp(code);
else
    disp('未能提取信息');
end

%%
string_code = string (code);
%display(string_code);

pattern_getcode = '```matlab\s*(.*?)\s*```'; % 匹配代码块
matches_getcode = regexp(code, pattern_getcode, 'tokens');

% 检查是否找到了匹配
if ~isempty(matches_getcode)
    % 提取第一个匹配的代码块
    codeBlock = matches_getcode{1}{1};
    
    % 打印提取的代码块（可选）
    disp('提取的代码块:');
    disp(codeBlock);
    
    % 使用 eval 执行提取的代码
    eval(codeBlock);
else
    disp('未找到 MATLAB 代码块。');
end
