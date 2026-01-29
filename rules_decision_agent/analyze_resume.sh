#!/bin/bash
# 便捷启动脚本 - DeepSeek 简历分析

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate

# 运行 DeepSeek 简历分析
python scripts/run_deepseek_resume.py "$@"
