# Polyphony Steps and Plan

## Core Direction
Polyphony is an AI Creative Operating System, not just an editor.
We will build it in small, understandable slices.

## Working Process
1. Define one small milestone before coding.
2. Explain where it fits in the architecture.
3. Create only the minimum files needed.
4. Understand every line before moving on.
5. Test the flow.
6. Revise the plan if needed.

## Layer Map
- Understanding Layer: what the system sees and detects
- Reasoning Layer: what the system thinks and plans
- Execution Layer: what tools actually perform
- Creative Brain: orchestration and creative suggestions
- Memory: decisions, preferences, history
- Production Layer: projects, sessions, uploads, outputs

## Current Milestone
Milestone 1: project/session backbone plus image upload.

### Goal
Create the smallest backend foundation for:
- creating a project
- creating a session
- uploading an image asset

### Not In Scope Yet
- region detection
- editing tools
- LangGraph workflows
- voice
- video/audio analysis
- memory personalization

## First Build Order
1. backend app entrypoint
2. config/settings
3. database connection
4. project and session models
5. image upload route
6. basic verification

## Learning Rule
If any file or line is unclear, we stop and explain it before adding more.
