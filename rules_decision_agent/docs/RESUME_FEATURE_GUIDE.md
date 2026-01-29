# 简历问答提取功能 - 安装和测试指南

## 快速开始

### 1. 安装依赖

由于您的系统使用外部管理的 Python 环境，您需要使用虚拟环境：

```bash
# 导航到项目目录
cd /Users/elonxu/Desktop/decision-agent-demo/rules_decision_agent

# 创建虚拟环境（如果尚未创建）
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt
```

### 2. 设置环境变量

确保您有一个包含 Google API 密钥的 `.env` 文件：

```bash
# 如果不存在，创建 .env 文件
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### 3. 测试简历功能

#### 选项 A：CLI 模式（推荐首次测试）

```bash
# 确保虚拟环境已激活
source .venv/bin/activate

# 使用示例简历运行
python run_resume.py examples/sample_resume.txt
```

预期输出：
- 候选人信息（姓名、邮箱等）
- 专业总结
- 技能列表
- 分类的面试问题和建议答案
- JSON 输出文件：`resume_analysis_output.json`

#### 选项 B：A2A API 模式

终端 1 - 启动服务器：
```bash
source .venv/bin/activate
python run_a2a.py
```

终端 2 - 测试 API：
```bash
# 上传简历
curl -X POST http://localhost:8001/resume/extract \
  -F "file=@examples/sample_resume.txt"

# 检查支持的格式
curl http://localhost:8001/resume/formats
```

### 4. 使用您自己的简历测试

```bash
# 使用 PDF
python run_resume.py /path/to/your/resume.pdf

# 使用 DOCX
python run_resume.py /path/to/your/resume.docx

# 使用 TXT
python run_resume.py /path/to/your/resume.txt
```

## 故障排除

### 问题："ModuleNotFoundError: No module named 'PyPDF2'"
**解决方案**：确保您已激活虚拟环境并安装了依赖：
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 问题："GOOGLE_API_KEY not found"
**解决方案**：创建一个包含您的 API 密钥的 `.env` 文件：
```bash
echo "GOOGLE_API_KEY=your_actual_api_key" > .env
```

### 问题：PDF 解析失败
**解决方案**：确保 PyPDF2 已正确安装：
```bash
pip install --upgrade PyPDF2
```

### 问题：DOCX 解析失败
**解决方案**：确保 python-docx 已安装：
```bash
pip install --upgrade python-docx
```

## 运行测试

```bash
# 如果尚未安装 pytest，请安装
pip install pytest pytest-asyncio

# 运行测试
pytest test_resume.py -v
```

## 预期结果

简历处理器将：
1. **解析**简历文件（PDF/DOCX/TXT）
2. **提取**结构化信息：
   - 个人信息（姓名、邮箱、电话、位置）
   - 专业总结
   - 技能和技术
   - 工作经验
   - 教育背景
   - 项目
3. **生成** 4 个类别的面试问题：
   - **技术技能**：关于特定技术的问题
   - **行为问题**：基于经验的 STAR 格式问题
   - **项目深入探讨**：详细的项目问题
   - **问题解决**：基于场景的问题
4. **提供**基于简历内容的建议答案

## 示例输出结构

```json
{
  "success": true,
  "candidateInfo": {
    "name": "张三",
    "email": "zhangsan@email.com",
    "phone": "+86-138-0000-0000",
    "location": "北京"
  },
  "summary": "拥有 5 年以上经验的高级软件工程师...",
  "extractedData": {
    "skills": ["Python", "JavaScript", "React", "AWS"],
    "experience": [...],
    "education": [...],
    "projects": [...]
  },
  "questionsAndAnswers": [
    {
      "category": "技术技能",
      "questions": [
        {
          "question": "您能解释一下使用 Python 和 Django 的经验吗？",
          "suggestedAnswer": "我在 Python 方面有丰富的经验...",
          "difficulty": "中级",
          "relatedSkills": ["Python", "Django", "FastAPI"]
        }
      ]
    }
  ]
}
```
