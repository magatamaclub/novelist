# 小说家俱乐部 (Novelist Club)

一个基于多Agent协同的自动小说创作系统。

## 项目结构

```
novelist/
├── agents/                # Agent实现
│   ├── creator_agent.py   # 故事创意生成器
│   ├── writer_agent.py    # 小说创作者
│   ├── supervisor_agent.py # 故事监制
│   └── editor_agent.py    # 文字编辑
├── core/                  # 核心功能模块
│   ├── workflow.py        # 工作流控制
│   └── logging.py         # 日志系统
├── configs/               # 配置文件
│   └── story_seed.yaml    # 故事种子配置
├── outputs/               # 输出目录
│   ├── outlines/          # 故事大纲
│   ├── drafts/           # 小说草稿
│   └── logs/             # 系统日志
└── app.py                # 主程序入口
```

## 系统流程

1. **故事构思**: 创意生成器(CreatorAgent)根据故事种子配置生成故事大纲
2. **内容创作**: 小说作家(WriterAgent)根据大纲进行创作
3. **情节审核**: 故事监制(SupervisorAgent)审核内容逻辑和合理性
4. **文字优化**: 文字编辑(EditorAgent)进行校对和润色

整个过程是一个循环，直到产出符合要求的作品。每个Agent的工作记录都会通过日志系统详细记录。

## 配置文件说明

故事种子配置文件(story_seed.yaml)包含：
- 基本信息（标题、主题）
- 故事背景设定
- 人物设定
- 情节要素
- 写作风格偏好

## 使用方法

1. 配置Python环境（要求Python 3.9+）
2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 准备故事种子配置文件：
```yaml
# configs/story_seed.yaml
title: "故事标题"
theme: "故事主题"
...
```

4. 运行程序：
```bash
python -m novelist.app
```

## 输出说明

- outlines/: 存放生成的故事大纲（YAML格式）
- drafts/: 存放小说草稿和最终稿（TXT格式）
- logs/: 存放系统运行日志，记录每个Agent的工作过程

## 待开发功能

- [ ] 接入大模型API进行智能创作
- [ ] 增加更多写作风格选项
- [ ] 支持多种输出格式（Markdown、PDF等）
- [ ] 提供Web界面进行配置和监控
- [ ] 增加更多类型的写作模板

## 贡献指南

欢迎提交Issue和Pull Request来完善项目。

## 开源协议

MIT License
