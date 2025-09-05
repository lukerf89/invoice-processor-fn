# Manual Agent Setup Guide - Invoice Processing

## Overview

Since Claude Code CLI needs to be installed separately, here are the manual setup commands to create your three-agent development pipeline once you have the CLI available.

## Prerequisites

1. **Install Claude Code CLI**:
   ```bash
   # Visit: https://docs.anthropic.com/claude/docs/claude-code
   # Follow installation instructions for your platform
   ```

2. **Verify Installation**:
   ```bash
   claude-code --version
   ```

## Agent Creation Commands

Navigate to your project directory and run these commands:

```bash
cd /Volumes/Working/Code/GoogleCloud/invoice-processor-fn
```

### 1. Create Technical PM Agent (Opus 4.1)

```bash
claude-code agent create technical-pm \
  --model claude-opus-4-20250805 \
  --instructions .claude/agents/technical-pm/instructions.md \
  --context "docs/prds/,docs/architecture/universal-engineering-principles.md,CLAUDE.md" \
  --description "Technical Product Manager for translating PRDs into executable phase documents for invoice processing systems"
```

### 2. Create Senior Engineer Agent (Opus 4.1)

```bash
claude-code agent create senior-engineer \
  --model claude-opus-4-20250805 \
  --instructions .claude/agents/senior-engineer/instructions.md \
  --context "docs/architecture/universal-engineering-principles.md,CLAUDE.md" \
  --description "Senior Engineer for breaking down phase documents into TDD tasks with algorithmic patterns"
```

### 3. Create Coding Agent (Sonnet 4)

```bash
claude-code agent create coding-agent \
  --model claude-sonnet-4-20250514 \
  --instructions .claude/agents/coding-agent/instructions.md \
  --context "main.py,test_scripts/,CLAUDE.md" \
  --description "Coding agent for implementing TDD tasks with algorithmic invoice processing patterns"
```

### 4. Verify Agent Setup

```bash
claude-code agent list
```

## Custom Slash Commands (Quick Access)

Once agents are created, you can use convenient slash commands for faster development:

### Available Slash Commands

**Descriptive Commands:**
- `/product-manager` - Create comprehensive PRDs from business requirements
- `/technical-pm` - Translate PRDs into executable phase documents  
- `/senior-engineer` - Break down phases into atomic TDD tasks
- `/coding-agent` - Implement TDD tasks using Red-Green-Refactor methodology

**Short Commands (Aliases):**
- `/pm` - Quick product-manager access
- `/se` - Quick senior-engineer access  
- `/ca` - Quick coding-agent access

### Usage Examples

```bash
# Create a PRD from business requirements
/pm "Create PRD for improving Creative-Coop invoice processing accuracy from 85% to 95%"

# Break down a phase document into TDD tasks
/se "Analyze docs/phases/phase-01-creative-coop-critical-fix.md and create comprehensive TDD task breakdown"

# Implement specific tasks
/ca "Implement Task 09 from .claude/tasks/pending/ following Red-Green-Refactor methodology"

# Create technical implementation plan
/technical-pm "Convert the Creative-Coop column alignment PRD into detailed phase documents with risk assessment"
```

### Slash Command Setup

The slash commands are automatically configured via files in `.claude/commands/`:
- `.claude/commands/product-manager.md`
- `.claude/commands/technical-pm.md`  
- `.claude/commands/senior-engineer.md`
- `.claude/commands/coding-agent.md`
- `.claude/commands/pm.md` (short version)
- `.claude/commands/se.md` (short version)
- `.claude/commands/ca.md` (short version)

## Usage Commands (Alternative)

If slash commands aren't working, use these full commands for your development workflow:

### Step 1: PRD to Phase Document (Technical PM)
```bash
claude-code agent run technical-pm \
  "Please analyze the PRD in docs/prds/ and create a comprehensive Phase 1 implementation plan for invoice processing improvements. Focus on AI service integration, vendor pattern development, and performance optimization within Zapier timeout constraints."
```

### Step 2: Phase to Tasks (Senior Engineer)
```bash
claude-code agent run senior-engineer \
  "Please analyze the phase document in docs/phases/ and create detailed TDD task breakdowns for invoice processing components. Ensure all processing uses algorithmic patterns, not hardcoded values."
```

### Step 3: Task Implementation (Coding Agent)
```bash
claude-code agent run coding-agent \
  "Please implement the task in .claude/tasks/pending/ following TDD methodology with algorithmic patterns. Ensure compliance with Zapier timeout limits and multi-tier AI processing."
```

### Step 4: Code Review (Senior Engineer)
```bash
claude-code agent run senior-engineer \
  "Please review the implementation focusing on algorithmic processing patterns, AI service integration, and compliance with Universal Engineering Principles."
```

## File Structure Verification

Ensure these files exist before running agent creation:

### Agent Configuration Files
- `.claude/agents/technical-pm/instructions.md` ✅
- `.claude/agents/technical-pm/phase-document-template.md` ✅  
- `.claude/agents/technical-pm/risk-assessment-framework.md` ✅
- `.claude/agents/senior-engineer/instructions.md` ✅
- `.claude/agents/senior-engineer/task-template.md` ✅
- `.claude/agents/senior-engineer/invoice-processing-patterns.md` ✅
- `.claude/agents/coding-agent/instructions.md` ✅

### Slash Command Files (Auto-configured)
- `.claude/commands/product-manager.md` ✅ (Auto-created)
- `.claude/commands/technical-pm.md` ✅ (Auto-created) 
- `.claude/commands/senior-engineer.md` ✅ (Auto-created)
- `.claude/commands/coding-agent.md` ✅ (Auto-created)
- `.claude/commands/pm.md` ✅ (Short alias)
- `.claude/commands/se.md` ✅ (Short alias) 
- `.claude/commands/ca.md` ✅ (Short alias)

### Documentation Files
- `docs/SETUP - Technical PM Agent.md` ✅
- `docs/SETUP - Sr Engineer Agent.md` ✅
- `docs/architecture/universal-engineering-principles.md` ✅
- `CLAUDE.md` ✅

### Working Directories
- `docs/prds/` ✅ (place PRDs here)
- `docs/phases/` ✅ (generated phase documents)
- `.claude/tasks/pending/` ✅
- `.claude/tasks/in-progress/` ✅
- `.claude/tasks/completed/` ✅

## Development Workflow

1. **Place PRD** in `docs/prds/` directory
2. **Run Technical PM Agent** to create phase document
3. **Run Senior Engineer Agent** to break down into TDD tasks
4. **Run Coding Agent** to implement each task
5. **Run Senior Engineer Agent** for code review
6. **Iterate** until production ready

## Success Indicators

After setup, you should be able to:
- ✅ List all three agents with `claude-code agent list`
- ✅ Use slash commands like `/pm`, `/se`, `/ca` for quick agent access
- ✅ Run Technical PM agent to create phase documents from PRDs
- ✅ Run Senior Engineer agent to create TDD tasks from phases
- ✅ Run Coding Agent to implement tasks with algorithmic patterns
- ✅ Complete full PRD → Phase → Tasks → Implementation → Review pipeline

## Troubleshooting

### Agent Creation Fails
- Verify file paths are correct (use absolute paths if needed)
- Check that all instruction files exist and are readable
- Ensure Claude Code CLI has proper permissions

### Context Files Not Found
- Verify CLAUDE.md exists in project root
- Check that docs/architecture/universal-engineering-principles.md exists
- Ensure main.py exists for coding agent context

### Model Not Available
- Check model names are correct and available in your Claude Code plan
- Try alternative model versions if needed

### Slash Commands Not Working
- Verify `.claude/commands/` directory exists with all 7 command files
- Check that command files have `.md` extension and correct content
- Test with a simple command like `/pm "test"` to verify recognition
- Fallback to full `claude-code agent run` commands if needed

## Next Steps

Once agents are created successfully:

1. Create your first PRD in `docs/prds/`
2. Test the complete pipeline with a simple invoice processing improvement
3. Validate each agent produces expected output format
4. Begin implementing your actual invoice processing improvements

The complete three-agent ecosystem is now ready for invoice processing development with full TDD methodology, algorithmic pattern requirements, and AI service integration focus!