# AdvisorStyle Agent

> AI-powered Academic Writing Assistant with Supervisor Style Modeling

---

## Overview

AdvisorStyle Agent is an AI-assisted academic writing system built with Codex and LLMs.

The project aims to help researchers improve academic writing quality by learning the writing style of a specific supervisor (or academic author) and applying it to paper revision and structure optimization.

The system combines:

- Codex-based writing workflow
- LLM-powered style analysis
- Zotero API integration
- Academic writing optimization

---

## Core Features

### 1. Supervisor Style Modeling

Analyze papers from a target supervisor and extract:

- Sentence structure patterns
- Academic tone
- Logical organization style
- Writing preferences

---

### 2. Academic Writing Assistant

Rewrite paper drafts based on extracted style features.

Functions include:

- Academic polishing
- Structural optimization
- Tone consistency
- Writing clarity enhancement

---

### 3. Zotero Integration

Integrate Zotero API for:

- Literature organization
- Citation workflow
- Academic reference management

---

### 4. Codex-based Workflow

Use Codex for:

- Paper structure generation
- Writing assistance
- LaTeX/code support
- Prompt-driven revision workflow

---

## System Workflow

```text
Supervisor Papers
        ↓
Style Analysis (LLM)
        ↓
Writing Style Profile
        ↓
Paper Draft Input
        ↓
Rewrite & Optimization
        ↓
Improved Academic Paper
```

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | GPT / DeepSeek |
| Workflow | Codex |
| Backend | Python |
| UI | Streamlit |
| Reference System | Zotero API |
| Prompting | Prompt Engineering |

---

## Project Structure

```text
advisor-style-agent/
│
├── app.py
├── README.md
├── requirements.txt
│
├── llm/
│   ├── style_analyzer.py
│   └── rewrite_engine.py
│
├── prompts/
│   ├── style_prompt.txt
│   └── rewrite_prompt.txt
│
└── data/
    └── supervisor_papers/
```

---

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the project

```bash
streamlit run app.py
```

---

## Example Use Case

1. Upload supervisor papers
2. Extract writing style profile
3. Input paper draft
4. Generate revised academic version

---

## Current Progress

- Prototype completed
- Codex writing workflow tested
- Zotero API workflow explored
- Style modeling experiments ongoing

---

## Future Work

- Multi-supervisor style comparison
- Citation optimization
- Full agent workflow
- LaTeX paper generation
- Long-context academic memory

---

## Motivation

This project explores how LLMs and AI agents can improve personalized academic writing workflows while maintaining consistency with supervisor writing styles.

---

## License

MIT License
