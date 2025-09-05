# Invoice Processing Agent Setup

## Quick Start for New Developers

This repository includes a complete 4-agent development pipeline for invoice processing improvements.

### Prerequisites
- Node.js 18+
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- Claude.ai account

### Agent Setup (5 minutes)

1. **Clone and navigate**:
   ```bash
   git clone [repo-url]
   cd invoice-processor-fn
   ```

2. **Run automated setup**:
   ```bash
   ./setup-agents.sh
   ```

3. **Verify agents are created**:
   ```bash
   claude-code agent list
   ```

You should see 4 agents:
- `product-manager` (orange) - Creates PRDs from business requirements
- `technical-pm` (blue) - Creates phase documents from PRDs
- `senior-engineer` (green) - Creates TDD tasks from phase documents
- `coding-agent` (purple) - Implements tasks with algorithmic patterns

## Development Workflow

### Complete Pipeline
```bash
# 1. Create PRD from business requirements
claude-code agent run product-manager \
  "Analyze [problem] and create comprehensive PRD"

# 2. Create phase document
claude-code agent run technical-pm \
  "Create Phase 1 implementation plan from the PRD"

# 3. Break down into tasks
claude-code agent run senior-engineer \
  "Create detailed TDD task breakdowns from phase document"

# 4. Implement solution
claude-code agent run coding-agent \
  "Implement task using algorithmic patterns and TDD methodology"
```

### Quick Start Examples
```bash
# Improve vendor processing accuracy
claude-code agent run product-manager \
  "We need to improve Creative-Coop processing accuracy from 75% to 90%"

# Add new vendor support
claude-code agent run product-manager \
  "We need to add support for [VendorName] invoices"

# Performance optimization
claude-code agent run product-manager \
  "Processing is taking too long, need to optimize for Zapier timeouts"
```

## Agent Specializations

### Product Manager Agent 🟠
- **Purpose**: Business requirements → PRDs
- **Input**: Business problems, stakeholder needs
- **Output**: Comprehensive PRDs with success criteria
- **Maintains**: Product backlog and roadmap

### Technical PM Agent 🔵
- **Purpose**: PRDs → Phase documents
- **Input**: Product requirements documents
- **Output**: Detailed implementation phases with risk assessment
- **Specializes**: AI service integration, performance planning

### Senior Engineer Agent 🟢
- **Purpose**: Phase documents → TDD tasks
- **Input**: Implementation phase plans
- **Output**: Atomic tasks with comprehensive test specifications
- **Ensures**: Algorithmic patterns, engineering best practices

### Coding Agent 🟣
- **Purpose**: Tasks → Implementation
- **Input**: TDD task specifications
- **Output**: Tested, production-ready code
- **Follows**: Red-Green-Refactor methodology, no hardcoding

## Troubleshooting

### Agent Creation Fails
- Verify Claude Code CLI is installed and authenticated
- Check file paths in setup script are correct
- Ensure you're in the project root directory

### Agents Not Listed
```bash
# Check agent status
claude-code agent list

# Recreate specific agent
claude-code agent create [agent-name] --instructions .claude/agents/[agent-name].md
```

### Getting Help
- See `docs/SETUP - *.md` files for detailed documentation
- Check `CLAUDE.md` for project-specific context
- Review existing PRDs in `docs/prds/` for examples

## File Structure
```
.claude/agents/           # Agent configuration files
├── product-manager.md    # PM agent configuration
├── technical-pm.md       # Technical PM configuration
├── senior-engineer.md    # Senior engineer configuration
└── coding-agent.md       # Coding agent configuration

docs/
├── prds/                 # Generated PRDs
├── phases/               # Generated phase documents
└── SETUP - *.md          # Detailed setup guides
```

This agent ecosystem provides a complete business-to-code pipeline specifically optimized for invoice processing improvements with AI service integration.
