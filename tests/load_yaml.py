import yaml
from types import SimpleNamespace

def dict_to_namespace(d):
    """递归将 dict 转成支持属性访问的对象"""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [dict_to_namespace(x) for x in d]
    else:
        return d

def load_agents_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return dict_to_namespace(data)

# 使用示例
if __name__ == "__main__":
    agents_cfg = load_agents_yaml("configs/agents.yaml")
    
    # 访问示例
    print(agents_cfg.agents.web_search.model)
    print(agents_cfg.agents.web_search.instructions, type(agents_cfg.agents.web_search.instructions)) # str
    print(agents_cfg.agents.news_search.instructions, type(agents_cfg.agents.news_search.instructions)) # list
    print(agents_cfg.prompts.search_prompt)

    from pprint import pprint
    pprint(agents_cfg)