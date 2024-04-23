# LLM Context

LLM Context is a Python application that helps users easily collect and prepare code snippets for pasting into chat conversations with language models like ChatGPT.

It allows users to select multiple files, processes them using customizable Jinja2 templates, and automatically copies the formatted output to the clipboard for easy pasting.

The code in this repository was developed in collaboration with Claude 3 Opus. 

## Features

- Select multiple files using a graphical file selector
- Process selected files using customizable Jinja2 templates
- Automatically copy the formatted output to the clipboard

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/llm-context.git
   ```

2. Change to the project directory:
   ```
   cd llm-context
   ```

3. Install the required dependencies using Poetry:
   ```
   poetry install
   ```

## Usage

1. Run the application:
   ```
   poetry run python src/select_files.py
   ```

2. Click the "Select Files" button in the file selector window and choose the files you want to process.

3. Run the application:
   ```
   poetry run python src/main.py
   ```

4. The selected files will be processed using the configured Jinja2 template, and the formatted output will be automatically copied to your clipboard.

5. Paste the formatted code into your chat conversation with the language model.

## Configuration

LLM Context uses two configuration files:

- Global configuration (`~/.llm-context/config.json`): Contains global settings like the current project root path and templates folder path.
- Project configuration (`.llm-context/config.json`): Contains project-specific settings like the the selected files and current template.

The default configurations are:

Global configuration:
```json
{
  "root_path": "~/Github/my-project-name",
  "templates_path": "~/Github/llm-context/templates"
}
```

Project configuration:
```json
{
  "template": "all-file-contents.jinja",
  "files": []
}
```

You can modify these configurations to suit your needs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or find any bugs.