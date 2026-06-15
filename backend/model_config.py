"""
模型配置管理模块
- 从 .env 读取 MODEL_N_* 配置
- 写入/更新/删除 .env 中的模型配置
- 测试模型连通性
- 脱敏返回 API Key
"""
import os
import re
import copy
from dotenv import load_dotenv, set_key, unset_key

ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')

load_dotenv(ENV_PATH, override=True)

_models_cache = None


def _clear_cache():
    global _models_cache
    _models_cache = None


def _parse_models():
    """扫描环境变量，解析所有 MODEL_N_* 配置"""
    global _models_cache
    if _models_cache is not None:
        return _models_cache

    # 先清除所有旧的 MODEL_ 环境变量，避免删除后残留
    pattern_clean = re.compile(r'^MODEL_\d+_(NAME|PROVIDER|API_KEY|BASE_URL|MODEL)$')
    for key in list(os.environ.keys()):
        if pattern_clean.match(key):
            del os.environ[key]

    load_dotenv(ENV_PATH, override=True)
    pattern = re.compile(r'^MODEL_(\d+)_(NAME|PROVIDER|API_KEY|BASE_URL|MODEL)$')
    groups = {}

    for key, value in os.environ.items():
        m = pattern.match(key)
        if m:
            idx = m.group(1)
            field = m.group(2).lower()
            groups.setdefault(idx, {})[field] = value

    models = []
    for idx in sorted(groups.keys(), key=int):
        cfg = groups[idx]
        models.append({
            'id': f'model_{idx}',
            'index': int(idx),
            'name': cfg.get('name', ''),
            'provider': cfg.get('provider', 'openai').lower().strip(),
            'api_key': cfg.get('api_key', ''),
            'base_url': cfg.get('base_url', ''),
            'model': cfg.get('model', ''),
        })

    _models_cache = models
    return models


def _mask_key(key):
    """脱敏 API Key：保留前4位和后4位"""
    if not key or len(key) <= 8:
        return '****' if key else ''
    return key[:4] + '*' * (len(key) - 8) + key[-4:]


def get_available_models():
    """返回可用模型列表（不含敏感信息，仅 api_key 非空的）"""
    all_models = _parse_models()
    return [{'id': m['id'], 'name': m['name'], 'provider': m['provider']}
            for m in all_models if m['api_key']]


def get_model_params(model_id):
    """根据 model_id 返回完整配置（含 api_key）"""
    for m in _parse_models():
        if m['id'] == model_id:
            return m
    return None


def get_all_model_configs():
    """返回所有模型配置（API Key 脱敏）"""
    models = _parse_models()
    result = []
    for m in models:
        result.append({
            'id': m['id'],
            'name': m['name'],
            'provider': m['provider'],
            'api_key_masked': _mask_key(m['api_key']),
            'api_key_set': bool(m['api_key']),
            'base_url': m['base_url'],
            'model': m['model'],
        })
    return result


def save_model_config(model_id, name, provider, api_key, base_url, model_name):
    """保存单个模型配置到 .env"""
    idx = model_id.replace('model_', '') if model_id.startswith('model_') else model_id

    # 如果 model_id 为 "new"，自动分配新编号
    if model_id == 'new':
        existing = _parse_models()
        existing_ids = [m['index'] for m in existing]
        idx = str(max(existing_ids, default=0) + 1)

    prefix = f'MODEL_{idx}'
    set_key(ENV_PATH, f'{prefix}_NAME', name)
    set_key(ENV_PATH, f'{prefix}_PROVIDER', provider)
    set_key(ENV_PATH, f'{prefix}_BASE_URL', base_url)
    set_key(ENV_PATH, f'{prefix}_MODEL', model_name)

    # API Key 只在非空时写入（避免覆盖）
    if api_key and api_key != '****':
        set_key(ENV_PATH, f'{prefix}_API_KEY', api_key)

    _clear_cache()
    load_dotenv(ENV_PATH, override=True)
    return f'model_{idx}'


def delete_model_config(model_id):
    """从 .env 中删除指定模型配置"""
    idx = model_id.replace('model_', '') if model_id.startswith('model_') else model_id
    prefix = f'MODEL_{idx}'
    for suffix in ['NAME', 'PROVIDER', 'API_KEY', 'BASE_URL', 'MODEL']:
        unset_key(ENV_PATH, f'{prefix}_{suffix}')
    _clear_cache()
    load_dotenv(ENV_PATH, override=True)


def test_model_connectivity(model_id):
    """
    测试模型连通性：发送一条简单消息，检查是否能正常返回。
    返回 (success: bool, message: str)
    """
    from llm_client import call_llm

    cfg = get_model_params(model_id)
    if not cfg:
        return False, f'模型 {model_id} 未找到'
    if not cfg['api_key']:
        return False, 'API Key 未配置'
    if not cfg['base_url']:
        return False, 'Base URL 未配置'
    if not cfg['model']:
        return False, '模型名称未配置'

    try:
        messages = [
            {"role": "system", "content": "你是一个助手。"},
            {"role": "user", "content": "请回复'连接成功'两个字。"}
        ]
        result = call_llm(
            provider=cfg['provider'],
            api_key=cfg['api_key'],
            base_url=cfg['base_url'],
            model=cfg['model'],
            messages=messages,
            max_tokens=20,
            temperature=0.1
        )
        if result:
            return True, f'连通成功: {result[:50]}'
        else:
            return False, '模型返回为空'
    except Exception as e:
        return False, f'连接失败: {str(e)[:200]}'
