# Novelist - AI驱动的小说创作系统

一个基于多Agent协同的自动小说创作系统，使用 DeepSeek 模型实现智能创作。

## 功能特点

- 多角色协同：创意生成、写作、审核、编辑
- 基于 DeepSeek 大模型
- 可自定义故事设定
- 完整的日志记录
- 自动保存创作成果
- 智能评分和修订系统
- 错别字自动检查
- 多轮创作优化

## 安装步骤

1. 克隆项目：
```bash
git clone [项目地址]
cd novelist
```

2. 创建并激活虚拟环境（推荐）：
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. 安装依赖：
```bash
# 安装基本依赖
pip install -e .

# 如需运行测试，安装测试依赖
pip install -r tests/requirements-test.txt
```

## 配置

1. 创建环境变量文件：
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入您的配置
vim .env
```

2. 在 .env 文件中配置：
```ini
# API配置
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# 工作流控制配置
MAX_REVISION_CYCLES=3       # 最大修订轮次
MAX_EDITING_CYCLES=2        # 最大润色轮次
REVISION_SCORE_THRESHOLD=80 # 内容评分达标线（0-100）
```

## 运行

1. 基本运行：
```bash
# 确保在项目根目录
python -m novelist

# 或使用安装后的命令
novelist
```

2. 自定义故事设定：
   - 编辑 `novelist/configs/story_seed.yaml` 文件
   - 修改标题、人物、情节等设定

3. 查看输出：
   - 最终故事：`novelist/outputs/outlines/`
   - 故事草稿：`novelist/outputs/drafts/`
   - 运行日志：`novelist/outputs/logs/`

## 运行测试

1. 安装测试依赖：
```bash
pip install -r tests/requirements-test.txt
```

2. 运行测试：
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_workflow_integration.py  # 集成测试
pytest tests/test_creator_agent.py        # 创意生成器测试
pytest tests/test_writer_agent.py         # 写作者测试
pytest tests/test_supervisor_agent.py     # 监制测试
pytest tests/test_editor_agent.py         # 编辑测试

# 按标记运行测试
pytest -m asyncio      # 异步测试
pytest -m unit        # 单元测试
pytest -m integration # 集成测试

# 生成覆盖率报告
pytest --cov=novelist  # 终端报告
pytest --cov=novelist --cov-report=html  # HTML报告
```

3. 查看测试报告：
   - 终端输出显示测试结果和覆盖率
   - HTML报告位于 `tests/coverage_html/`
   - 日志文件位于 `novelist/outputs/logs/`

## 项目结构

```
novelist/
├── novelist/          # 主代码目录
│   ├── agents/       # AI角色实现
│   │   ├── creator_agent.py    # 创意生成器
│   │   ├── writer_agent.py     # 写作者
│   │   ├── supervisor_agent.py # 故事监制
│   │   └── editor_agent.py     # 文字编辑
│   ├── configs/      # 配置文件
│   ├── core/         # 核心功能
│   │   ├── workflow.py   # 工作流管理
│   │   ├── adapter.py    # Agent适配器
│   │   └── llm_factory.py # LLM工厂
│   └── outputs/      # 输出目录
│       ├── outlines/ # 最终故事
│       ├── drafts/   # 故事草稿
│       └── logs/     # 运行日志
├── tests/            # 测试用例
└── .env.example      # 环境变量示例
```

## 工作流程

1. 创意生成：由creator生成故事大纲
2. 内容创作：writer根据大纲进行创作
3. 质量评估：supervisor评估内容质量，打分0-100
   - 0分：完全偏离大纲，退回重写
   - 1-79分：需要修改和润色
   - 80-100分：通过，完成创作
4. 文字优化：editor检查错别字和文字润色
5. 循环优化：未达标则返回步骤2继续改进

## 常见问题

1. ModuleNotFoundError：
```bash
pip install -e ".[test]"  # 安装所有依赖
```

2. API错误：检查 .env 文件中的配置
```bash
cat .env  # 确认API密钥正确
```

3. 权限问题：确保outputs目录可写
```bash
chmod -R 755 novelist/outputs/  # Linux/Mac
```

4. 测试失败：
```bash
# 检查测试环境
pytest --collect-only  # 检查测试收集
pytest -v             # 详细输出
```

## 开发计划

- [x] 多轮创作优化系统
- [x] 自动错别字检查
- [x] 完整测试覆盖
- [ ] 支持更多写作风格
- [ ] 增加角色对话生成
- [ ] 添加情节智能推荐
- [ ] Web界面支持

## 许可证

MIT License
