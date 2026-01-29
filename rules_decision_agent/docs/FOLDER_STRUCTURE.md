# 📁 项目文件夹结构说明

本文档说明了项目的文件夹组织结构。

## 📂 目录结构

```
rules_decision_agent/
├── 📄 README.md                    # 项目主文档
├── 📄 requirements.txt             # Python 依赖包列表
├── 📄 .env                         # 环境变量配置（API keys）
├── 📄 .gitignore                   # Git 忽略文件配置
│
├── 📁 src/                         # 源代码目录
│   ├── agent.py                    # 决策代理核心逻辑
│   ├── resume_agent.py             # Google Gemini 简历分析代理
│   ├── deepseek_resume_agent.py    # DeepSeek 简历分析代理
│   └── __init__.py                 # Python 包初始化文件
│
├── 📁 scripts/                     # 运行脚本目录
│   ├── run_direct.py               # 直接运行决策代理（CLI）
│   ├── run_a2a.py                  # A2A 服务器模式
│   ├── run_resume.py               # Gemini 简历分析（CLI）
│   ├── run_deepseek_resume.py      # DeepSeek 简历分析（CLI）
│   └── inspect_agent.py            # 代理检查工具
│
├── 📁 tests/                       # 测试文件目录
│   ├── test_a2a.py                 # A2A 协议测试
│   ├── test_resume.py              # 简历分析测试
│   └── test_api_config.py          # API 配置验证
│
├── 📁 docs/                        # 文档目录
│   ├── DEEPSEEK_GUIDE.md           # DeepSeek 使用指南
│   ├── DEEPSEEK_INTEGRATION_SUMMARY.md  # DeepSeek 集成总结
│   ├── RESUME_FEATURE_GUIDE.md     # 简历功能指南
│   ├── implementation_plan.md      # 实现计划
│   ├── walkthrough.md              # 项目演练文档
│   ├── task.md                     # 任务说明
│   └── *.metadata.json             # 元数据文件
│
├── 📁 examples/                    # 示例文件目录
│   └── sample_resume.txt           # 示例简历
│
└── 📁 outputs/                     # 输出文件目录
    ├── .gitkeep                    # Git 保留空目录
    ├── deepseek_resume_analysis_output.json
    └── resume_analysis_output.json
```

## 📋 目录说明

### `src/` - 源代码
存放所有核心业务逻辑代码：
- **agent.py**: 决策代理的核心实现
- **resume_agent.py**: 使用 Google Gemini 的简历分析
- **deepseek_resume_agent.py**: 使用 DeepSeek 的简历分析

### `scripts/` - 运行脚本
存放所有可执行的入口脚本：
- **run_direct.py**: 直接运行决策代理
- **run_a2a.py**: 启动 A2A 服务器
- **run_resume.py**: Gemini 简历分析 CLI
- **run_deepseek_resume.py**: DeepSeek 简历分析 CLI（推荐）
- **inspect_agent.py**: 代理检查工具

### `tests/` - 测试
存放所有测试文件：
- **test_a2a.py**: A2A 协议测试客户端
- **test_resume.py**: 简历分析功能测试
- **test_api_config.py**: API 配置验证工具

### `docs/` - 文档
存放所有项目文档：
- **DEEPSEEK_GUIDE.md**: DeepSeek 详细使用指南
- **DEEPSEEK_INTEGRATION_SUMMARY.md**: DeepSeek 集成总结
- **RESUME_FEATURE_GUIDE.md**: 简历分析功能指南
- **implementation_plan.md**: 项目实现计划
- **walkthrough.md**: 项目演练和架构说明
- **task.md**: 任务说明

### `examples/` - 示例
存放示例文件和数据：
- **sample_resume.txt**: 示例简历文件

### `outputs/` - 输出
存放程序运行生成的输出文件：
- JSON 格式的分析结果
- 日志文件等

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
编辑 `.env` 文件，添加 API keys：
```bash
GOOGLE_API_KEY=your_google_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 3. 运行测试
```bash
# 测试 API 配置
python tests/test_api_config.py

# 测试简历分析（DeepSeek）
python scripts/run_deepseek_resume.py examples/sample_resume.txt
```

## 📝 命名规范

- **源代码**: `snake_case.py`
- **脚本**: `run_*.py` 或 `test_*.py`
- **文档**: `UPPERCASE.md` 或 `lowercase.md`
- **配置**: `.env`, `.gitignore`

## 🔄 迁移说明

如果你有旧的脚本或代码引用了原来的文件路径，需要更新为：

### 运行脚本
```bash
# 旧路径
python run_deepseek_resume.py examples/sample_resume.txt

# 新路径
python scripts/run_deepseek_resume.py examples/sample_resume.txt
```

### 测试脚本
```bash
# 旧路径
python test_api_config.py

# 新路径
python tests/test_api_config.py
```

## 💡 最佳实践

1. **源代码** 只放在 `src/` 目录
2. **可执行脚本** 放在 `scripts/` 目录
3. **测试文件** 放在 `tests/` 目录
4. **文档** 放在 `docs/` 目录
5. **输出文件** 自动保存到 `outputs/` 目录
6. **不要提交** `.env` 文件和 `outputs/` 中的 JSON 文件到 Git

## 🔗 相关文档

- [主 README](../README.md) - 项目总览
- [DeepSeek 使用指南](docs/DEEPSEEK_GUIDE.md)
- [简历功能指南](docs/RESUME_FEATURE_GUIDE.md)
