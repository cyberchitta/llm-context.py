import pytest

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
        {"include_style": False, "include_template_logic": False},
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
        {"include_style": True, "include_template_logic": False},
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
        {"include_style": False, "include_template_logic": True},
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
        {"include_style": False, "include_template_logic": False},
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
        {"include_style": True, "include_template_logic": True},
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
        {"include_style": False, "include_template_logic": False},
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
    assert actual_output == expected_output, (
        f"Mismatch in {test_name}:\nExpected:\n{expected_output}\n\nActual:\n{actual_output}"
    )


def test_svelte_empty_file():
    """Test handling of empty Svelte files."""
    source = Source("empty.svelte", "")
    excerpter = Sfc({"include_style": False, "include_template_logic": False})

    result = excerpter.excerpt([source])

    # Based on the actual behavior, empty files produce "⋮..." content
    assert len(result.excerpts) == 1
    assert result.excerpts[0].content.strip() == "⋮..."


def test_svelte_non_svelte_file():
    """Test that non-Svelte files are ignored."""
    source = Source("test.js", "console.log('hello');")
    excerpter = Sfc({"include_style": False, "include_template_logic": False})

    result = excerpter.excerpt([source])

    # Should not process non-Svelte files
    assert len(result.excerpts) == 0


def test_multiple_svelte_files():
    """Test processing multiple Svelte files."""
    sources = [
        Source("App.svelte", """<script>let name = 'App';</script><div>{name}</div>"""),
        Source("Button.svelte", """<script>export let label;</script><button>{label}</button>"""),
    ]
    excerpter = Sfc({"include_style": False, "include_template_logic": False})

    result = excerpter.excerpt(sources)

    assert len(result.excerpts) == 2
    paths = {excerpt.rel_path for excerpt in result.excerpts}
    assert paths == {"App.svelte", "Button.svelte"}
