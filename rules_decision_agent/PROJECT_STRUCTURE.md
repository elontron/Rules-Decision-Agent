# 📁 项目结构说明

项目已重新组织，结构更加清晰。

## 🗂️ 新的文件夹结构

```
rules_decision_agent/
├── 📄 README.md                    # 项目主文档
├── 📄 requirements.txt             # Python 依赖
├── 📄 .env                         # 环境变量（API keys）
├── 📄 .gitignore                   # Git 忽略配置
├── 📄 analyze_resume.sh            # 快捷启动脚本
│
├── 📁 src/                         # 源代码
│   ├── agent.py
│   ├── resume_agent.py
│   └── deepseek_resume_agent.py
│
├── 📁 scripts/                     # 运行脚本
│   ├── run_direct.py
│   ├── run_a2a.py
│   ├── run_resume.py
│   ├── run_deepseek_resume.py
│   └── inspect_agent.py
│
├── 📁 tests/                       # 测试文件
│   ├── test_a2a.py
│   ├── test_resume.py
│   └── test_api_config.py
│
├── 📁 docs/                        # 文档
│   ├── DEEPSEEK_GUIDE.md
│   ├── RESUME_FEATURE_GUIDE.md
│   ├── FOLDER_STRUCTURE.md
│   └── ...
│
├── 📁 examples/                    # 示例文件
│   └── sample_resume.txt
│
└── 📁 outputs/                     # 输出文件
    └── *.json
```

## 🚀 快速使用

### 方式 1: 使用便捷脚本
```bash
./analyze_resume.sh examples/sample_resume.txt
```

### 方式 2: 直接运行
```bash
source .venv/bin/activate

# DeepSeek 简历分析（推荐）
python scripts/run_deepseek_resume.py examples/sample_resume.txt

# Google Gemini 简历分析
python scripts/run_resume.py examples/sample_resume.txt

# 决策代理
python scripts/run_direct.py "Your prompt here"

# A2A 服务器
python scripts/run_a2a.py
```

### 测试 API 配置
```bash
python tests/test_api_config.py
```

## 📝 主要变化

| 旧路径 | 新路径 |
|--------|--------|
| `run_deepseek_resume.py` | `scripts/run_deepseek_resume.py` |
| `test_api_config.py` | `tests/test_api_config.py` |
| `DEEPSEEK_GUIDE.md` | `docs/DEEPSEEK_GUIDE.md` |
| `deepseek_resume_analysis_output.json` | `outputs/deepseek_resume_analysis_output.json` |

## 📚 详细文档

- [文件夹结构详解](docs/FOLDER_STRUCTURE.md)
- [DeepSeek 使用指南](docs/DEEPSEEK_GUIDE.md)
- [简历功能指南](docs/RESUME_FEATURE_GUIDE.md)
- [主 README](README.md)

## ✨ 优势

- ✅ **分类清晰** - 代码、脚本、测试、文档分离
- ✅ **易于维护** - 文件组织有序
- ✅ **便于查找** - 快速定位所需文件
- ✅ **规范化** - 符合 Python 项目最佳实践
