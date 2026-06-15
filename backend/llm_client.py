"""
统一 LLM 调用抽象模块
支持 OpenAI 兼容接口和 Anthropic 接口。
"""
from openai import OpenAI
import anthropic


def call_llm(provider, api_key, base_url, model, messages, max_tokens=500, temperature=0.7):
    """
    统一调用 LLM。

    Args:
        provider: "openai" 或 "anthropic"
        api_key: API 密钥
        base_url: API 基础地址
        model: 模型名称
        messages: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        max_tokens: 最大输出 token 数
        temperature: 温度参数

    Returns:
        str: 模型输出文本
    """
    provider = provider.lower().strip()

    if provider == "openai":
        return _call_openai(api_key, base_url, model, messages, max_tokens, temperature)
    elif provider == "anthropic":
        return _call_anthropic(api_key, base_url, model, messages, max_tokens, temperature)
    else:
        raise ValueError(f"不支持的 provider: {provider}，仅支持 'openai' 或 'anthropic'")


def _call_openai(api_key, base_url, model, messages, max_tokens, temperature):
    """调用 OpenAI 兼容接口（适用于 OpenAI / GLM / 小米 / Minimax 等）"""
    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    content = resp.choices[0].message.content
    if content is None:
        # 某些模型可能把内容放在 reasoning_content 中
        content = getattr(resp.choices[0].message, 'reasoning_content', '') or ''
    return content.strip()


def _call_anthropic(api_key, base_url, model, messages, max_tokens, temperature):
    """调用 Anthropic 接口（兼容 ThinkingBlock / TextBlock 混合响应）"""
    client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

    # Anthropic 的 system 是顶层参数，不是 message
    system_text = ""
    user_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            user_messages.append(msg)

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": user_messages,
    }
    if system_text:
        kwargs["system"] = system_text

    resp = client.messages.create(**kwargs)

    # 遍历 content 块，找到 TextBlock（有 .text 属性的）
    # 跳过 ThinkingBlock（没有 .text 属性）
    text_parts = []
    for block in resp.content:
        if hasattr(block, 'text'):
            text_parts.append(block.text)

    if text_parts:
        return "".join(text_parts).strip()

    # 兜底：如果全是 ThinkingBlock 没有 TextBlock，尝试从 thinking 属性获取
    for block in resp.content:
        if hasattr(block, 'thinking'):
            text_parts.append(block.thinking)

    return "".join(text_parts).strip() if text_parts else "模型未返回文本内容"
