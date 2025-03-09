# Novelist - AI驱动的小说创作系统

一个基于多Agent协同的自动小说创作系统，使用 DeepSeek 模型实现智能创作。

## 功能特点

- 多角色协同：创意生成、写作、审核、编辑
- 基于 DeepSeek 大模型
- 可自定义故事设定
- 完整的日志记录
- 自动保存创作成果

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

# 如需运行测试，安装完整依赖
pip install -e ".[test]"
```

## 配置

1. 创建环境变量文件：
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入您的 DeepSeek API 密钥
vim .env
```

2. 在 .env 文件中配置：
```
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
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
   - 故事草稿：`novelist/outputs/drafts/`
   - 运行日志：`novelist/outputs/logs/`

## 运行测试

```bash
# 运行所有测试
pytest tests/

# 带覆盖率报告
pytest --cov=novelist tests/
```

## 项目结构

```
novelist/
├── novelist/          # 主代码目录
│   ├── agents/       # AI角色实现
│   ├── configs/      # 配置文件
│   ├── core/         # 核心功能
│   └── outputs/      # 输出目录
└── tests/            # 测试用例
```

## 常见问题

1. ModuleNotFoundError：确保已正确安装所有依赖
   ```bash
   pip install -e ".[test]"
   ```

2. API错误：检查 .env 文件中的 API 密钥配置

3. 权限问题：确保 outputs 目录可写

## 开发计划

- [ ] 支持更多写作风格
- [ ] 增加角色对话生成
- [ ] 添加情节智能推荐
- [ ] Web界面支持

## 许可证

MIT License
