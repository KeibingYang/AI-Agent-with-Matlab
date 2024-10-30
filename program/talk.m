system_prompt = "You are a helpful assistant. You might get a context for each question, but only use the information in the context if that makes sense to answer the question. ";
chat = ollamaChat("llama3", system_prompt);

%%配置模型
%设置每次聊天会话允许的最大字数，并定义关键字，当用户输入该关键字时，该关键字将结束聊天会话。
wordLimit = 2000;
stopWord = "end";

%创建一个实例ollamaChat来执行聊天，创建一个实例messageHistory来存储会话历史记录。
%chat = ollamaChat("qwen2:7b");
messages = messageHistory;

%% 聊天循环
% 开始聊天并保持聊天，直到出现stopWord设置的语句出现
totalWords = 0;
messagesSizes = [];
%% 
% 主循环会无限地继续下去，直到输入设置好的stopWord或按下Ctrl+ c 
while true
    query = input("User: ", "s");
    query = string(query);
    %dispWrapped("User", query)
%% 
% 如果您输入了stopWord，则显示消息并退出循环。

    if query == stopWord
        disp("AI: Closing the chat. Have a great day!")
        break;
    end

    numWordsQuery = countNumWords(query);
%% 
% 如果查询超过字数限制，则显示错误消息并停止执行。

    if numWordsQuery>wordLimit
        error("Your query should have fewer than " + wordLimit + " words. You query had " + numWordsQuery + " words.")
    end
%% 
% 跟踪每条消息的大小和到目前为止使用的总字数。

    messagesSizes = [messagesSizes; numWordsQuery]; %#ok
    totalWords = totalWords + numWordsQuery;
%% 
% 如果总字数超过限制，则从会话开始时删除消息，直到不再使用为止。

    while totalWords > wordLimit
        totalWords = totalWords - messagesSizes(1);
        messages = removeMessage(messages, 1);
        messagesSizes(1) = [];
    end
%% 
% 将新消息添加到会话并生成新的响应。

    messages = addUserMessage(messages, query);
    [text, response] = generate(chat, messages);
  
    dispWrapped("AI", text)
%% 
% 计算回复中的字数并更新总字数。

    numWordsResponse = countNumWords(text);
    messagesSizes = [messagesSizes; numWordsResponse]; %#ok
    totalWords = totalWords + numWordsResponse;
%% 
% 向会话添加响应。

    messages = addResponseMessage(messages, response);
end
%% |Helper Functions|
% 该函数用于计算文本字符串中的单词数

function numWords = countNumWords(text)
    numWords = doclength(tokenizedDocument(text));
end
%% 
% 该函数显示从前缀挂起缩进的换行文本

function dispWrapped(prefix, text)
    indent = [newline, repmat(' ',1,strlength(prefix)+2)];
    text = strtrim(text);
    disp(prefix + ": " + join(textwrap(text, 70),indent))
end
%% 
