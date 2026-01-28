import pytest

from llm_context.excerpters.markdown import Markdown
from llm_context.excerpters.parser import Source
from llm_context.excerpters.sfc import Sfc

# Test cases: (test_name, extension, code, config, expected_output)
TEST_CASES = [
    (
        "svelte_script_only",
        "svelte",
        """<script>
  let name = 'world';
  
  function handleClick() {
    name = 'Svelte';
  }
  
  export let title;
</script>

<style>
  h1 {
    color: #ff3e00;
    font-size: 2rem;
  }
  
  .button {
    padding: 0.5rem 1rem;
    border: none;
  }
</style>

<h1>Hello {name}!</h1>
<button class="button" on:click={handleClick}>
  Click me
</button>

{#if title}
  <h2>{title}</h2>
{/if}""",
        {"with-style": False, "with-template": False},
        """<script>
  let name = 'world';
  
  function handleClick() {
    name = 'Svelte';
  }
  
  export let title;
</script>
⋮...
<style>
⋮...
</style>
⋮...""",
    ),
    (
        "svelte_with_style",
        "svelte",
        """<script>
  let theme = 'dark';
  let count = 0;
</script>

<style>
  .container {
    background: var(--bg-color);
    padding: 1rem;
  }
  
  .dark {
    --bg-color: #333;
    color: white;
  }
  
  .counter {
    font-size: 1.2rem;
    margin: 1rem 0;
  }
</style>

<div class="container {theme}">
  <p class="counter">Count: {count}</p>
  <button on:click={() => count++}>+</button>
</div>""",
        {"with-style": True, "with-template": False},
        """<script>
  let theme = 'dark';
  let count = 0;
</script>
⋮...
<style>
  .container {
    background: var(--bg-color);
    padding: 1rem;
  }
  
  .dark {
    --bg-color: #333;
    color: white;
  }
  
  .counter {
    font-size: 1.2rem;
    margin: 1rem 0;
  }
</style>
⋮...""",
    ),
    (
        "svelte_with_template",
        "svelte",
        """<script>
  let items = ['apple', 'banana', 'cherry'];
  let showList = true;
</script>

<style>
  .list-item { 
    margin: 0.5rem; 
    padding: 0.25rem;
  }
  
  .hidden { display: none; }
</style>

{#if showList}
  <ul>
    {#each items as item, index}
      <li class="list-item">{index + 1}: {item}</li>
    {/each}
  </ul>
{:else}
  <p>List is hidden</p>
{/if}

<button on:click={() => showList = !showList}>
  Toggle list
</button>""",
        {"with-style": False, "with-template": True},
        """<script>
  let items = ['apple', 'banana', 'cherry'];
  let showList = true;
</script>

<style>
⋮...
</style>

{#if showList}
  <ul>
    {#each items as item, index}
      <li class="list-item">{index + 1}: {item}</li>
    {/each}
  </ul>
{:else}
  <p>List is hidden</p>
{/if}

<button on:click={() => showList = !showList}>
  Toggle list
</button>""",
    ),
    (
        "svelte_typescript",
        "svelte",
        """<script lang="ts">
  interface User {
    name: string;
    age: number;
  }
  
  let user: User = {
    name: 'Alice',
    age: 30
  };
  
  function greet(user: User): string {
    return `Hello, ${user.name}!`;
  }
</script>

<style>
  .greeting { 
    color: blue; 
    font-weight: bold;
  }
</style>

<div class="greeting">
  {greet(user)}
  <p>Age: {user.age}</p>
</div>""",
        {"with-style": False, "with-template": False},
        """<script lang="ts">
  interface User {
    name: string;
    age: number;
  }
  
  let user: User = {
    name: 'Alice',
    age: 30
  };
  
  function greet(user: User): string {
    return `Hello, ${user.name}!`;
  }
</script>
⋮...
<style>
⋮...
</style>
⋮...""",
    ),
    (
        "svelte_all_sections",
        "svelte",
        """<script>
  export let title = 'Component';
  let count = 0;
  
  $: doubled = count * 2;
</script>

<style>
  .title { 
    font-size: 2rem; 
    color: #333;
  }
  
  .count { 
    color: #666; 
  }
</style>

<div>
  <h1 class="title">{title}</h1>
  <p class="count">Count: {count}</p>
  <p>Doubled: {doubled}</p>
  
  {#if count > 5}
    <p>High count!</p>
  {/if}
  
  <button on:click={() => count++}>Increment</button>
</div>""",
        {"with-style": True, "with-template": True},
        """<script>
  export let title = 'Component';
  let count = 0;
  
  $: doubled = count * 2;
</script>

<style>
  .title { 
    font-size: 2rem; 
    color: #333;
  }
  
  .count { 
    color: #666; 
  }
</style>

<div>
  <h1 class="title">{title}</h1>
  <p class="count">Count: {count}</p>
  <p>Doubled: {doubled}</p>
  
  {#if count > 5}
    <p>High count!</p>
  {/if}
  
  <button on:click={() => count++}>Increment</button>
</div>""",
    ),
    (
        "svelte_module_script",
        "svelte",
        """<script context="module">
  export function preload(page) {
    return { 
      props: { 
        data: page.query.data || 'default' 
      } 
    };
  }
  
  let moduleCounter = 0;
</script>

<script>
  export let data;
  
  let instanceCount = 0;
  
  function processData(raw) {
    return raw.toUpperCase();
  }
</script>

<style>
  .content { 
    padding: 1rem; 
  }
</style>

<div class="content">
  <p>Data: {processData(data)}</p>
  <p>Instance: {instanceCount}</p>
</div>""",
        {"with-style": False, "with-template": False},
        """<script context="module">
  export function preload(page) {
    return { 
      props: { 
        data: page.query.data || 'default' 
      } 
    };
  }
  
  let moduleCounter = 0;
</script>
⋮...
<script>
  export let data;
  
  let instanceCount = 0;
  
  function processData(raw) {
    return raw.toUpperCase();
  }
</script>
⋮...
<style>
⋮...
</style>
⋮...""",
    ),
]


@pytest.mark.parametrize("test_name,extension,code,config,expected_output", TEST_CASES)
def test_svelte_excerpting(test_name, extension, code, config, expected_output):
    source = Source(f"test_file.{extension}", code)
    excerpter = Sfc(config)

    result = excerpter.excerpt([source])

    assert len(result.excerpts) == 1
    assert result.excerpts[0].rel_path == f"test_file.{extension}"

    actual_output = result.excerpts[0].content.strip()
    assert (
        actual_output == expected_output
    ), f"Mismatch in {test_name}:\nExpected:\n{expected_output}\n\nActual:\n{actual_output}"


def test_svelte_empty_file():
    """Test handling of empty Svelte files."""
    source = Source("empty.svelte", "")
    excerpter = Sfc({"with-style": False, "with-template": False})

    result = excerpter.excerpt([source])

    # Based on the actual behavior, empty files produce "⋮..." content
    assert len(result.excerpts) == 1
    assert result.excerpts[0].content.strip() == "⋮..."


def test_svelte_non_svelte_file():
    """Test that non-Svelte files are ignored."""
    source = Source("test.js", "console.log('hello');")
    excerpter = Sfc({"with-style": False, "with-template": False})

    result = excerpter.excerpt([source])

    # Should not process non-Svelte files
    assert len(result.excerpts) == 0


def test_multiple_svelte_files():
    """Test processing multiple Svelte files."""
    sources = [
        Source("App.svelte", """<script>let name = 'App';</script><div>{name}</div>"""),
        Source("Button.svelte", """<script>export let label;</script><button>{label}</button>"""),
    ]
    excerpter = Sfc({"with-style": False, "with-template": False})

    result = excerpter.excerpt(sources)

    assert len(result.excerpts) == 2
    paths = {excerpt.rel_path for excerpt in result.excerpts}
    assert paths == {"App.svelte", "Button.svelte"}


MARKDOWN_TEST_CASES = [
    (
        "markdown_all_elements",
        "md",
        """# Main Heading

This is the first paragraph that should be included.

## Subheading

Another paragraph to filter out.

- List item one
- List item two
- List item three

```python
def hello():
    print("Hello, World!")
```

> This is a blockquote
> with multiple lines

---

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

Final paragraph to filter.""",
        {
            "with-code-blocks": True,
            "with-lists": True,
            "with-tables": True,
            "with-blockquotes": True,
            "with-thematic-breaks": True,
        },
        """# Main Heading

⋮...
## Subheading

⋮...
- List item one
- List item two
- List item three

```python
def hello():
    print("Hello, World!")
```

> This is a blockquote
> with multiple lines

---

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |""",
    ),
    (
        "markdown_headings_only",
        "md",
        """# Getting Started

Learn how to use this tool.

## Installation

Run this command to install.

```bash
npm install
```

## Usage

Here's how to use it.

- Step 1
- Step 2

### Advanced

More details here.""",
        {
            "with-code-blocks": False,
            "with-lists": False,
            "with-tables": False,
            "with-blockquotes": False,
            "with-thematic-breaks": False,
        },
        """# Getting Started

⋮...
## Installation

⋮...
## Usage

⋮...
### Advanced""",
    ),
    (
        "markdown_with_code_only",
        "md",
        """# Documentation

This intro paragraph is included.

## Code Examples

Here's some code that should be included:

```javascript
const x = 42;
console.log(x);
```

More prose that gets excluded.

```python
def example():
    return True
```

Final paragraph excluded.""",
        {
            "with-code-blocks": True,
            "with-lists": False,
            "with-tables": False,
            "with-blockquotes": False,
            "with-thematic-breaks": False,
        },
        """# Documentation

⋮...
## Code Examples

⋮...
```javascript
const x = 42;
console.log(x);
```

⋮...
```python
def example():
    return True
```""",
    ),
    (
        "markdown_lists_tables",
        "md",
        """# Data Management

Overview paragraph here.

## Configuration Options

- Option A
- Option B
- Option C

Some explanatory text.

| Option | Value | Description |
|--------|-------|-------------|
| A      | 1     | First       |
| B      | 2     | Second      |

More info excluded.""",
        {
            "with-code-blocks": False,
            "with-lists": True,
            "with-tables": True,
            "with-blockquotes": False,
            "with-thematic-breaks": False,
        },
        """# Data Management

⋮...
## Configuration Options

- Option A
- Option B
- Option C

Some explanatory text.
| Option | Value | Description |
|--------|-------|-------------|
| A      | 1     | First       |
| B      | 2     | Second      |""",
    ),
    (
        "markdown_blockquotes_breaks",
        "md",
        """# Important Notes

Read this carefully.

## Warnings

> **Warning:** This is critical
> Do not ignore this

---

## Information

> This is informational
> Take note

Some additional text excluded.""",
        {
            "with-code-blocks": False,
            "with-lists": False,
            "with-tables": False,
            "with-blockquotes": True,
            "with-thematic-breaks": True,
        },
        """# Important Notes

⋮...
## Warnings

> **Warning:** This is critical
> Do not ignore this

---

## Information

> This is informational
> Take note""",
    ),
    (
        "markdown_setext_headings",
        "md",
        """Main Title
===========

This paragraph is included.

Subsection
----------

Text to filter out.

Another subsection
------------------

More excluded text.""",
        {
            "with-code-blocks": True,
            "with-lists": True,
            "with-tables": True,
            "with-blockquotes": True,
            "with-thematic-breaks": True,
        },
        """Main Title
===========

⋮...
Subsection
----------

⋮...
Another subsection
------------------""",
    ),
]


@pytest.mark.parametrize("test_name,extension,code,config,expected_output", MARKDOWN_TEST_CASES)
def test_markdown_excerpting(test_name, extension, code, config, expected_output):
    source = Source(f"test_file.{extension}", code)
    excerpter = Markdown(config)

    result = excerpter.excerpt([source])

    assert len(result.excerpts) == 1
    assert result.excerpts[0].rel_path == f"test_file.{extension}"

    actual_output = result.excerpts[0].content.strip()
    assert (
        actual_output == expected_output
    ), f"Mismatch in {test_name}:\nExpected:\n{expected_output}\n\nActual:\n{actual_output}"


def test_markdown_empty_file():
    """Test handling of empty markdown files."""
    source = Source("empty.md", "")
    excerpter = Markdown(
        {
            "with-code-blocks": True,
            "with-first-paragraph": True,
            "with-lists": True,
            "with-tables": True,
            "with-blockquotes": True,
            "with-thematic-breaks": True,
        }
    )

    result = excerpter.excerpt([source])

    assert len(result.excerpts) == 1
    assert result.excerpts[0].content.strip() == ""


def test_markdown_non_markdown_file():
    """Test that non-markdown files are ignored."""
    source = Source("test.py", "print('hello')")
    excerpter = Markdown(
        {
            "with-code-blocks": True,
            "with-first-paragraph": True,
            "with-lists": True,
            "with-tables": True,
            "with-blockquotes": True,
            "with-thematic-breaks": True,
        }
    )

    result = excerpter.excerpt([source])

    assert len(result.excerpts) == 0


def test_markdown_multiple_files():
    """Test processing multiple markdown files."""
    sources = [
        Source(
            "README.md",
            """# Project

Overview here.

- Item 1
- Item 2""",
        ),
        Source(
            "GUIDE.md",
            """# Guide

Instructions here.

```bash
./run.sh
```""",
        ),
    ]
    excerpter = Markdown(
        {
            "with-code-blocks": True,
            "with-first-paragraph": True,
            "with-lists": True,
            "with-tables": True,
            "with-blockquotes": True,
            "with-thematic-breaks": True,
        }
    )

    result = excerpter.excerpt(sources)

    assert len(result.excerpts) == 2
    paths = {excerpt.rel_path for excerpt in result.excerpts}
    assert paths == {"README.md", "GUIDE.md"}


def test_markdown_metadata():
    """Test that metadata is correctly generated."""
    source = Source("test.md", "# Title\n\nContent")
    config = {
        "with-code-blocks": True,
        "with-first-paragraph": False,
        "with-lists": False,
        "with-tables": False,
        "with-blockquotes": False,
        "with-thematic-breaks": False,
    }
    excerpter = Markdown(config)

    result = excerpter.excerpt([source])

    assert len(result.excerpts) == 1
    metadata = result.excerpts[0].metadata
    assert metadata["processor_type"] == "markdown"
    assert "included_elements" in metadata
