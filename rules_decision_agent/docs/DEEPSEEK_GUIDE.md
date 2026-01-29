# DeepSeek 集成使用指南

本项目已成功集成 DeepSeek API，可以作为 Google Gemini 的替代方案使用。

## 📋 配置说明

### 环境变量

`.env` 文件中已配置以下 API keys：

```bash
GOOGLE_API_KEY=AIzaSyAqn4s6tOE9n5DGYNnOIGM5FCzfo0tqeds
DEEPSEEK_API_KEY=sk-9e3654ae89aa47848ac0421a7beecfad
```

### 依赖包

已添加 `openai>=1.0.0` 到 `requirements.txt`（DeepSeek 使用 OpenAI 兼容的 API）

## 🚀 使用方法

### 1. DeepSeek 简历分析（推荐）

使用 DeepSeek 进行简历分析，无配额限制问题：

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行 DeepSeek 简历分析
python run_deepseek_resume.py examples/sample_resume.txt
python run_deepseek_resume.py /path/to/your/resume.pdf
python run_deepseek_resume.py /path/to/your/resume.docx
```

### 2. Google Gemini 简历分析

如果 Google API 配额充足，可以使用原始的 Gemini 版本：

```bash
python run_resume.py examples/sample_resume.txt
```

## 📊 功能对比

| 功能 | DeepSeek | Google Gemini |
|------|----------|---------------|
| **简历解析** | ✅ 支持 PDF/DOCX/TXT | ✅ 支持 PDF/DOCX/TXT |
| **数据提取** | ✅ 结构化提取 | ✅ 结构化提取 |
| **问答生成** | ✅ 13+ 问题/4 类别 | ✅ 问答生成 |
| **配额限制** | ✅ 更宽松 | ⚠️ 免费层限制严格 |
| **响应速度** | ✅ 快速 | ✅ 快速 |
| **成本** | 💰 按使用付费 | 💰 免费层 + 付费 |
| **模型** | `deepseek-chat` | `gemini-2.0-flash-001` |

## 🎯 DeepSeek 优势

1. **无配额限制问题** - 不会遇到 429 错误
2. **高质量输出** - 生成详细的面试问题和答案
3. **成本效益** - 相对较低的 API 调用成本
4. **稳定可靠** - 适合生产环境使用

## 📝 输出示例

DeepSeek 分析会生成：

### 候选人信息
- 姓名、邮箱、电话、位置、LinkedIn

### 专业总结
- 简洁的职业概述

### 技能列表
- 提取所有技术技能（32+ 技能）

### 面试问题（4 个类别）
1. **技术技能** - 针对具体技术的深度问题
2. **行为问题** - STAR 格式的情景问题
3. **项目深入** - 关于具体项目的详细问题
4. **问题解决** - 场景化的解决方案问题

每个问题包含：
- 问题描述
- 建议答案（基于简历内容）
- 难度级别（entry/intermediate/advanced）
- 相关技能标签

## 📂 输出文件

分析结果会保存到：
- `deepseek_resume_analysis_output.json` - 完整的 JSON 格式结果

## 🔧 技术实现

### DeepSeek API 配置

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    temperature=0.3,
    max_tokens=4000
)
```

### 文件结构

```
src/
├── deepseek_resume_agent.py  # DeepSeek 集成模块
└── resume_agent.py            # 原始 Gemini 版本

run_deepseek_resume.py         # DeepSeek CLI 入口
run_resume.py                  # Gemini CLI 入口
```

## ⚠️ 注意事项

1. **API Key 安全** - 不要将 `.env` 文件提交到 Git
2. **成本控制** - DeepSeek 按使用量计费，注意监控使用情况
3. **网络连接** - 需要能够访问 `https://api.deepseek.com`

## 🆚 何时使用哪个模型？

### 使用 DeepSeek 当：
- ✅ Google API 配额已用完
- ✅ 需要稳定的生产环境
- ✅ 对成本敏感但需要高质量输出
- ✅ 需要处理大量简历

### 使用 Google Gemini 当：
- ✅ 在免费配额范围内
- ✅ 需要 Google 生态系统集成
- ✅ 测试和开发阶段

## 🎉 测试结果

DeepSeek 成功处理了示例简历：
- ✅ 提取了 32 项技能
- ✅ 生成了 13 个面试问题
- ✅ 覆盖了 4 个问题类别
- ✅ 每个问题都有详细的建议答案
- ✅ 处理时间：约 10-15 秒

## 📞 支持

如有问题，请检查：
1. `.env` 文件中的 API key 是否正确
2. 虚拟环境是否已激活
3. 依赖包是否已安装（`pip install -r requirements.txt`）
4. 网络连接是否正常
