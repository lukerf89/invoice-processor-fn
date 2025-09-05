#!/bin/bash

# Setup script for Invoice Processing Claude Code Agents
# This script initializes the Senior Engineer and Coding Agent configurations

echo "🚀 Setting up Invoice Processing Claude Code Agents (Full Stack)..."

# Check if Claude Code CLI is available
if ! command -v claude-code &> /dev/null; then
    echo "❌ Claude Code CLI not found. Please install it first."
    echo "   Visit: https://docs.anthropic.com/claude/docs/claude-code"
    exit 1
fi

echo "📋 Current directory: $(pwd)"

# 1. Create Technical PM Agent (Opus 4.1)
echo "📋 Creating Technical PM Agent..."
claude-code agent create technical-pm \
  --model claude-opus-4-20250805 \
  --instructions .claude/agents/technical-pm/instructions.md \
  --context "docs/prds/,docs/architecture/universal-engineering-principles.md,CLAUDE.md"

if [ $? -eq 0 ]; then
    echo "✅ Technical PM Agent created successfully"
else
    echo "❌ Failed to create Technical PM Agent"
    exit 1
fi

# 2. Create Senior Engineer Agent (Opus 4.1)
echo "🧠 Creating Senior Engineer Agent..."
claude-code agent create senior-engineer \
  --model claude-opus-4-20250805 \
  --instructions .claude/agents/senior-engineer/instructions.md \
  --context "docs/architecture/universal-engineering-principles.md,CLAUDE.md"

if [ $? -eq 0 ]; then
    echo "✅ Senior Engineer Agent created successfully"
else
    echo "❌ Failed to create Senior Engineer Agent"
    exit 1
fi

# 3. Create Coding Agent (Sonnet 4)  
echo "👨‍💻 Creating Coding Agent..."
claude-code agent create coding-agent \
  --model claude-sonnet-4-20250514 \
  --instructions .claude/agents/coding-agent/instructions.md \
  --context "main.py,test_scripts/,CLAUDE.md"

if [ $? -eq 0 ]; then
    echo "✅ Coding Agent created successfully"
else
    echo "❌ Failed to create Coding Agent"
    exit 1
fi

# 4. Verify agent setup
echo "🔍 Verifying agent configuration..."
echo "📁 Directory structure:"
echo "  .claude/agents/technical-pm/"
ls -la .claude/agents/technical-pm/

echo "  .claude/agents/senior-engineer/"
ls -la .claude/agents/senior-engineer/

echo "  .claude/agents/coding-agent/"
ls -la .claude/agents/coding-agent/

echo "  docs/architecture/"
ls -la docs/architecture/

echo ""
echo "🎉 Complete Agent Ecosystem Setup Complete!"
echo ""
echo "📋 Three-Agent Development Pipeline:"
echo "1. Place PRDs in docs/prds/ directory"
echo ""
echo "2. Run Technical PM Agent to create phase documents:"
echo "   claude-code agent run technical-pm \\"
echo "     \"Create a comprehensive phase document from the PRD focusing on invoice processing improvements.\""
echo ""
echo "3. Run Senior Engineer Agent to break down tasks:"
echo "   claude-code agent run senior-engineer \\"
echo "     \"Analyze the phase document and create detailed TDD task breakdowns.\""
echo ""
echo "4. Run Coding Agent to implement tasks:"
echo "   claude-code agent run coding-agent \\"
echo "     \"Implement the task following TDD methodology with algorithmic patterns.\""
echo ""
echo "5. Use Senior Engineer for code review:"
echo "   claude-code agent run senior-engineer \\"
echo "     \"Review the implementation for algorithmic processing and AI integration.\""
echo ""
echo "📖 Documentation:"
echo "  - docs/SETUP - Technical PM Agent.md"
echo "  - docs/SETUP - Sr Engineer Agent.md"
echo ""
echo "🚀 Complete development pipeline: PRD → Phase → Tasks → Implementation → Review"