#!/usr/bin/env python3

"""
AI/SRE Portfolio - Tool Idea Generator
Transforms problems into tool ideas and generates code skeletons
"""

import json
import os
import sys
from datetime import datetime
import urllib.request


def log(msg):
    """Structured logging"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {msg}", flush=True)


def get_perplexity_response(prompt):
    """Call Perplexity API"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        log("❌ PERPLEXITY_API_KEY not set")
        return None

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a startup product designer for SRE tools. Design minimal, viable tool ideas that solve real problems."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.8,
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(
            "https://api.perplexity.ai/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('choices', [{}])[0].get('message', {}).get('content')
    except Exception as e:
        log(f"❌ Perplexity API error: {e}")
        return None


def generate_tool_idea(problem):
    """Generate a tool idea for a single problem"""
    problem_title = problem.get('problem_title') or problem.get('title', 'Unknown')
    log(f"💡 Generating tool for: {problem_title}")

    prompt = f"""
Given this SRE problem from the community:

**Problem**: {problem_title}
**Description**: {problem.get('description', '')}
**Severity**: {problem.get('severity', 'MEDIUM')}

Design a minimal, buildable tool that solves this. Focus on:
1. Core functionality (what does it do?)
2. MVP scope (what's the 3-day version?)
3. Tech stack (keep it simple: Python/Go + standard tools)
4. Success metric (how do you know it works?)
5. GitHub repo structure

Return as JSON with keys:
{{
  "tool_name": "...",
  "description": "...",
  "core_features": ["...", "..."],
  "tech_stack": {{"language": "...", "frameworks": ["..."]}},
  "mvp_scope": "...",
  "success_metric": "...",
  "repo_structure": {{"folders": ["..."], "key_files": ["..."]}}
}}
"""

    response = get_perplexity_response(prompt)
    if not response:
        return None

    # Parse JSON
    try:
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response

        tool = json.loads(json_str)
        tool['source_problem'] = problem.get('problem_title') or problem.get('title', 'Unknown')
        return tool
    except json.JSONDecodeError:
        log(f"⚠️  Could not parse tool JSON: {response[:200]}")
        return None


def generate_code_skeleton(tool):
    """Generate a basic code skeleton for the tool"""
    log(f"🏗️  Generating code for {tool['tool_name']}")

    prompt = f"""
Generate a minimal Python code skeleton for this tool:

**Tool**: {tool['tool_name']}
**Description**: {tool.get('description', '')}
**Features**: {', '.join(tool.get('core_features', []))}

Provide:
1. main.py — entry point with basic structure
2. config.py — configuration handling
3. requirements.txt — Python dependencies

Keep it VERY minimal (< 100 lines per file). Use logging and basic error handling.

Return as JSON:
{{
  "main.py": "...",
  "config.py": "...",
  "requirements.txt": "..."
}}
"""

    response = get_perplexity_response(prompt)
    if not response:
        return None

    try:
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        else:
            json_str = response

        code = json.loads(json_str)
        return code
    except json.JSONDecodeError:
        log(f"⚠️  Could not parse code JSON")
        return None


def save_tool_idea(tool, code, output_dir):
    """Save tool idea to structured files"""
    tool_name = tool['tool_name'].lower().replace(" ", "_")
    tool_dir = os.path.join(output_dir, tool_name)
    os.makedirs(tool_dir, exist_ok=True)

    # Save tool spec
    with open(os.path.join(tool_dir, "tool_spec.json"), 'w') as f:
        json.dump(tool, f, indent=2)

    # Save code skeleton
    if code:
        for filename, content in code.items():
            with open(os.path.join(tool_dir, filename), 'w') as f:
                f.write(content)

    log(f"✅ Saved tool: {tool_dir}")
    return tool_dir


def main():
    """Main tool generation pipeline"""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load latest problems
    problems_dir = os.path.join(repo_root, "problems")
    os.makedirs(problems_dir, exist_ok=True)

    # Find latest problems file
    problem_files = sorted([f for f in os.listdir(problems_dir) if f.startswith("problems_")])
    if not problem_files:
        log("❌ No problems file found. Run extract_problems.py first.")
        return 1

    latest_problem_file = os.path.join(problems_dir, problem_files[-1])

    try:
        with open(latest_problem_file, 'r') as f:
            data = json.load(f)
            problems = data.get('problems', [])
    except Exception as e:
        log(f"❌ Error reading problems file: {e}")
        return 1

    if not problems:
        log("⚠️  No problems to generate tools for")
        return 1

    log("=" * 50)
    log("🧠 Starting Tool Idea Generation")
    log("=" * 50)
    log(f"📋 Processing {len(problems)} problems")

    # Output directory
    tools_dir = os.path.join(repo_root, "tools")
    os.makedirs(tools_dir, exist_ok=True)

    generated_count = 0

    # Generate tool for each problem
    for problem in problems[:3]:  # Top 3 to start
        tool = generate_tool_idea(problem)
        if not tool:
            continue

        code = generate_code_skeleton(tool)
        save_tool_idea(tool, code, tools_dir)
        generated_count += 1

    log("=" * 50)
    log(f"✅ Generated {generated_count} tool ideas")
    log("=" * 50)

    return 0 if generated_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
