
import os
import time
from typing import Optional
from cozepy import COZE_CN_BASE_URL, Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType

# Coze API配置
coze_api_token = 'pat_0yXx4HYM2IAf1AzAO9K0RhjKZ58FWckSyNs1svMVohXOiPxD3C9KBscVKaKr0v8W'
coze_api_base = COZE_CN_BASE_URL
bot_id = '7490534349583597580'

# 初始化Coze客户端
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 2  # 重试间隔（秒）

def get_pest_control_advice(location: str, pest_type: str, retry_count: int = 0) -> str:
    """
    通过Coze API获取综合的病虫害防治建议，包含重试机制
    :param location: 地区名称
    :param pest_type: 检测到的病虫害类型
    :param retry_count: 当前重试次数
    :return: 防治建议文本
    """
    try:
        # 构建查询提示
        prompt = f"""请根据以下信息提供病虫害防治建议，要求以下列格式输出：

地区：{location}
病虫害类型：{pest_type}

===当前天气情况===
[请提供当前天气的详细描述]

===近7日天气预报===
[请提供未来7天的天气预报概况]

===近半年自然灾害情况===
[请说明该地区近半年是否发生过自然灾害，及其影响]

===病虫害说明===
[请详细说明该病虫害的特征、危害程度等信息]

===防治建议===
[请提供具体的防治措施和注意事项，包括：
1. 农药使用建议
2. 物理防治方法
3. 生物防治方法
4. 注意事项]

请确保信息准确、专业，并以友好易懂的方式表达。"""

        # 使用stream方法进行对话
        response_text = ""
        stream_error = False
        try:
            for event in coze.chat.stream(
                bot_id=bot_id,
                user_id='询问者',
                additional_messages=[Message.build_user_question_text(prompt)]
            ):
                if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                    response_text += event.message.content
                elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                    if response_text.strip():
                        return response_text
                    stream_error = True
        except Exception as stream_error:
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                return get_pest_control_advice(location, pest_type, retry_count + 1)
            raise stream_error

        if stream_error and retry_count < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return get_pest_control_advice(location, pest_type, retry_count + 1)

        return "抱歉，无法获取防治建议，API响应异常，请稍后重试。"

    except Exception as e:
        error_msg = str(e)
        if retry_count < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return get_pest_control_advice(location, pest_type, retry_count + 1)
        if "API key" in error_msg.lower():
            return "API密钥验证失败，请检查API配置。"
        elif "timeout" in error_msg.lower():
            return "连接超时，请检查网络连接后重试。"
        elif "rate limit" in error_msg.lower():
            return "已达到API调用限制，请稍后再试。"
        return f"获取防治建议时发生错误：{error_msg}。请联系技术支持。"