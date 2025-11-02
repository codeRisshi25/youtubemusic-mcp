# Contributing to YouTube Music MCP Server

First off, thank you for considering contributing to the YouTube Music MCP Server! 🎉

This document provides guidelines for contributing to this project. Following these guidelines helps maintain code quality and makes the review process smoother.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)

---

## Code of Conduct

This project adheres to a simple code of conduct:

- **Be respectful** and considerate in all interactions
- **Be collaborative** and open to feedback
- **Be constructive** when providing criticism
- **Focus on the code**, not the person

---

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:

1. **Search existing issues** to avoid duplicates
2. **Update to the latest version** to ensure the bug still exists
3. **Test with MCP Inspector** to isolate the issue

When creating a bug report, include:

- **Python version**: `python --version`
- **OS and version**: e.g., "Ubuntu 22.04", "macOS 14.1", "Windows 11"
- **Installation method**: pip install, from source, etc.
- **Authentication method**: OAuth or browser cookies
- **Steps to reproduce**:
  1. Step one
  2. Step two
  3. ...
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Error messages**: Complete error output (remove sensitive info)
- **Additional context**: Screenshots, logs, etc.

### Suggesting Features

Feature suggestions are welcome! Please:

1. **Check existing issues** for similar suggestions
2. **Clearly describe the use case** - why is this feature needed?
3. **Provide examples** of how it would work
4. **Consider alternatives** you've explored

### Code Contributions

We welcome code contributions! Areas where help is especially appreciated:

- **Bug fixes** - fixing reported issues
- **New tools** - adding YouTube Music features
- **Documentation** - improving guides and examples
- **Tests** - expanding test coverage
- **Performance** - optimizations and caching
- **Error handling** - better error messages and recovery

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/youtubemusic-mcp.git
cd youtubemusic-mcp
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .
```

### 3. Set Up Authentication

Create `browser.json` or `oauth.json` for testing (see [README](../README.md#-authentication-setup))

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 5. Make Your Changes

Edit the code, add tests, update documentation.

### 6. Test Your Changes

```bash
# Test with MCP Inspector
npx @modelcontextprotocol/inspector venv/bin/python server.py

# Test authentication
python3 -c "from ytmusicapi import YTMusic; yt = YTMusic('browser.json'); print('✅ Works')"

# Run the server directly
python server.py
```

---

## Pull Request Process

### Before Submitting

1. ✅ **Test thoroughly** - ensure your changes work
2. ✅ **Update documentation** - README, docstrings, etc.
3. ✅ **Follow coding standards** (see below)
4. ✅ **Run code formatters**:

   ```bash
   # Format with black (if installed)
   black server.py

   # Or manually format to PEP 8
   ```

5. ✅ **Check for sensitive data** - no API keys, tokens, or personal info

### Submitting the PR

1. **Push your branch**:

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub:

   - Use a clear, descriptive title
   - Reference any related issues: "Fixes #123" or "Relates to #456"
   - Describe what changed and why
   - Include screenshots/examples if relevant

3. **PR Description Template**:

   ```markdown
   ## Changes

   - Bullet point summary of changes

   ## Motivation

   Why was this change needed?

   ## Testing

   - [ ] Tested with MCP Inspector
   - [ ] Tested with Claude Desktop
   - [ ] Verified authentication works

   ## Related Issues

   Fixes #123

   ## Screenshots (if applicable)
   ```

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged!

---

## Coding Standards

### Python Style

- **Follow PEP 8** - Python's official style guide
- **Use type hints** where appropriate
- **Async/await** for all MCP handlers
- **Descriptive variable names** - `liked_songs` not `ls`

### Code Structure

```python
# Good: Clear, descriptive function name and docstring
async def handle_get_liked_songs_count() -> list[types.TextContent]:
    """
    Get the total count of songs in the user's liked songs library.

    Returns:
        TextContent with the song count

    Raises:
        RuntimeError: If ytmusic client is not initialized
    """
    yt = await initialize_ytmusic()
    # ... implementation
```

### Error Handling

Always provide helpful error messages:

```python
# Good: Specific error with actionable message
if not yt:
    raise RuntimeError(
        "YouTube Music client not initialized. "
        "Ensure browser.json or oauth.json exists."
    )

# Bad: Generic error
if not yt:
    raise RuntimeError("Not initialized")
```

### Comments

- **Explain "why", not "what"** - code should be self-documenting
- **Update comments** when changing code
- **Use docstrings** for functions and classes

```python
# Good: Explains the reason
# YouTube Music API returns a max of 25 items per request,
# so we need to paginate to get all results
for page in range(0, total_items, 25):
    results = yt.get_liked_songs(limit=25, offset=page)

# Bad: Obvious from code
# Loop through pages
for page in range(0, total_items, 25):
```

---

## Testing Guidelines

### Manual Testing

Before submitting a PR, test:

1. **MCP Inspector** - verify tool works in isolation

   ```bash
   npx @modelcontextprotocol/inspector venv/bin/python server.py
   ```

2. **Claude Desktop** - verify integration works end-to-end

3. **Edge cases**:
   - Empty library
   - Invalid queries
   - Network errors
   - Authentication failures

### Test Scenarios

When adding new tools, test:

- ✅ **Normal operation** - tool works with valid inputs
- ✅ **Invalid inputs** - handles bad parameters gracefully
- ✅ **Empty results** - works when API returns no data
- ✅ **Authentication errors** - clear error when not authenticated
- ✅ **API errors** - handles YouTube Music API failures

---

## Commit Message Guidelines

### Format

```
type(scope): brief description

Longer explanation if needed. Explain what changed and why,
not how (the code shows how).

Fixes #123
```

### Types

- **feat**: New feature (e.g., "feat(tools): add lyrics fetching tool")
- **fix**: Bug fix (e.g., "fix(auth): handle expired cookies gracefully")
- **docs**: Documentation (e.g., "docs(readme): add OAuth setup instructions")
- **refactor**: Code refactoring (e.g., "refactor(server): extract auth logic")
- **test**: Adding tests (e.g., "test(search): add search tool test cases")
- **chore**: Maintenance (e.g., "chore(deps): update ytmusicapi to 1.11.2")

### Examples

```bash
# Good commits
git commit -m "feat(tools): add get_playlist_details tool"
git commit -m "fix(auth): improve error message for missing browser.json"
git commit -m "docs(claude): add troubleshooting section for Windows"

# Bad commits
git commit -m "update stuff"
git commit -m "fix bug"
git commit -m "WIP"
```

---

## Adding New Tools

When adding a new MCP tool:

### 1. Define the Tool

Add to `list_tools()` in `server.py`:

```python
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        # ... existing tools
        types.Tool(
            name="your_new_tool",
            description="Clear description of what it does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param_name": {
                        "type": "string",
                        "description": "What this parameter does"
                    }
                },
                "required": ["param_name"]
            }
        )
    ]
```

### 2. Implement the Handler

Add to `call_tool()`:

```python
async def handle_your_new_tool(param_name: str) -> list[types.TextContent]:
    """
    Clear docstring explaining the tool.

    Args:
        param_name: Description of the parameter

    Returns:
        TextContent with the results
    """
    yt = await initialize_ytmusic()

    # Implementation
    result = yt.some_api_method(param_name)

    return [types.TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]
```

### 3. Add to call_tool Switch

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "your_new_tool":
        return await handle_your_new_tool(**arguments)
    # ... other tools
```

### 4. Document It

Add to README.md under "Available Tools" section with:

- Description
- Parameters
- Return format
- Example usage

### 5. Test It

Test with MCP Inspector and Claude Desktop.

---

## Questions?

If you have questions:

1. Check the [main README](../README.md)
2. Search [existing discussions](https://github.com/codeRisshi25/youtubemusic-mcp/discussions)
3. Open a new discussion or issue

---

**Thank you for contributing! 🎵**
