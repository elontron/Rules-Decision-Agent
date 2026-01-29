# 🚀 快速参考卡片

## 📁 项目结构一览

```
rules_decision_agent/
├── src/          # 源代码
├── scripts/      # 运行脚本
├── tests/        # 测试文件
├── docs/         # 文档
├── examples/     # 示例
└── outputs/      # 输出
```

## ⚡ 常用命令

### DeepSeek 简历分析（推荐）
```bash
# 方式 1: 快捷脚本
./analyze_resume.sh examples/sample_resume.txt

# 方式 2: 直接运行
python scripts/run_deepseek_resume.py examples/sample_resume.txt
```

### API 配置测试
```bash
python tests/test_api_config.py
```

### 决策代理
```bash
python scripts/run_direct.py "Your prompt here"
```

### A2A 服务器
```bash
python scripts/run_a2a.py
```

## 📚 重要文档

| 文档 | 路径 | 说明 |
|------|------|------|
| DeepSeek 指南 | `docs/DEEPSEEK_GUIDE.md` | DeepSeek 详细使用说明 |
| 项目结构 | `PROJECT_STRUCTURE.md` | 快速了解项目组织 |
| 整理总结 | `REORGANIZATION_SUMMARY.md` | 文件夹整理详情 |
| 目录树 | `DIRECTORY_TREE.txt` | 可视化目录结构 |

## 🔑 环境配置

编辑 `.env` 文件：
```bash
GOOGLE_API_KEY=your_google_key
DEEPSEEK_API_KEY=your_deepseek_key
```

## 📂 文件位置速查

| 类型 | 位置 |
|------|------|
| 源代码 | `src/*.py` |
| 运行脚本 | `scripts/run_*.py` |
| 测试 | `tests/test_*.py` |
| 文档 | `docs/*.md` |
| 输出 | `outputs/*.json` |

## ⭐ 推荐工作流

1. **测试配置**
   ```bash
   python tests/test_api_config.py
   ```

2. **分析简历**
   ```bash
   ./analyze_resume.sh examples/sample_resume.txt
   ```

3. **查看结果**
   ```bash
   cat outputs/deepseek_resume_analysis_output.json
   ```

## 🎯 快捷键提示

- `Ctrl+C` - 停止运行中的脚本
- `./analyze_resume.sh` - 最快的简历分析方式
- `ls outputs/` - 查看所有输出文件

## 💡 提示

- ✅ 使用 DeepSeek 避免 Google API 配额限制
- ✅ 输出文件自动保存到 `outputs/` 目录
- ✅ 所有文档都在 `docs/` 目录
- ✅ `.env` 文件不会被 Git 提交

---

**需要帮助？** 查看 `docs/DEEPSEEK_GUIDE.md` 或 `README.md`
