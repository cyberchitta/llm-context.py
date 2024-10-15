import argparse
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pyperclip  # type: ignore  # External library for clipboard operations
from jinja2 import Environment, FileSystemLoader  # For template rendering

# Importing necessary modules from the project
from llm_context.file_selector import FileSelector
from llm_context.folder_structure_diagram import get_annotated_fsd
from llm_context.highlighter.language_mapping import to_language
from llm_context.highlighter.outliner import generate_outlines
from llm_context.highlighter.parser import Source
from llm_context.project_settings import ProjectSettings, profile_feedback
from llm_context.utils import PathConverter, create_entry_point, safe_read_file


# Template class for rendering templates with Jinja2
@dataclass(frozen=True)
class Template:
    name: str  # Template file name
    context: dict  # Data context for rendering the template
    env: Environment  # Jinja2 Environment object for template handling

    # Static method to create a Template instance
    @staticmethod
    def create(name: str, context: dict, templates_path) -> "Template":
        env = Environment(loader=FileSystemLoader(str(templates_path)))  # Set up Jinja2 environment
        return Template(name, context, env)

    # Render the template with the given context
    def render(self) -> str:
        template = self.env.get_template(self.name)
        return template.render(**self.context)


# ContextCollector class for gathering project-related data
@dataclass(frozen=True)
class ContextCollector:
    settings: ProjectSettings  # Stores project settings and configurations

    # Static method to create a ContextCollector instance
    @staticmethod
    def create(settings: "ProjectSettings") -> "ContextCollector":
        return ContextCollector(settings)

    # Sample a few files from the project that are not already provided in full_abs
    def sample_file_abs(self, full_abs: list[str]) -> list[str]:
        all_abs = set(FileSelector.create(self.settings.project_root_path, [".git"]).get_files())
        incomplete_files = sorted(list(all_abs - set(full_abs)))  # Find files not in full_abs
        return random.sample(incomplete_files, min(2, len(incomplete_files)))  # Sample up to 2 files

    # Return file paths and their content
    def files(self, rel_paths: list[str]) -> list[dict[str, str]]:
        abs_paths = PathConverter.create(self.settings.project_root_path).to_absolute(rel_paths)  # Convert relative paths to absolute paths
        return [
            {"path": rel_path, "content": content}
            for rel_path, abs_path in zip(rel_paths, abs_paths)
            if (content := safe_read_file(abs_path)) is not None  # Read and include file content
        ]

    # Return outlines for provided relative file paths
    def outlines(self, rel_paths: list[str]) -> list[dict[str, str]]:
        abs_paths = PathConverter.create(self.settings.project_root_path).to_absolute(rel_paths)
        source_set = [
            Source(rel, content)
            for rel, abs_path in zip(rel_paths, abs_paths)
            if (content := safe_read_file(abs_path)) is not None
        ]
        return generate_outlines(source_set)  # Generate outlines for files

    # Generate a folder structure diagram with annotations
    def folder_structure_diagram(
        self, full_abs: list[str], outline_abs: list[str], no_media: bool
    ) -> str:
        return get_annotated_fsd(self.settings.project_root_path, full_abs, outline_abs, no_media)


# ContextGenerator class for producing context-based information
@dataclass(frozen=True)
class ContextGenerator:
    collector: ContextCollector  # Gathers context information
    settings: ProjectSettings  # Holds project configuration
    project_root: Path  # Root path of the project
    converter: PathConverter  # Path conversion utility
    full_rel: list[str]  # Full list of relative file paths
    full_abs: list[str]  # Full list of absolute file paths
    outline_rel: list[str]  # Relative paths for outlines
    outline_abs: list[str]  # Absolute paths for outlines

    # Static method to create a ContextGenerator instance
    @staticmethod
    def create() -> "ContextGenerator":
        settings = ProjectSettings.create()  # Load project settings
        collector = ContextCollector.create(settings)
        project_root = settings.project_root_path
        converter = PathConverter.create(project_root)  # Create a path converter
        sel_files = settings.context_storage.get_stored_context()  # Get stored context files
        full_rel = sel_files.get("full", [])  # Full files (relative paths)
        full_abs = converter.to_absolute(full_rel)  # Convert to absolute paths
        outline_rel = [f for f in sel_files.get("outline", []) if to_language(f)]  # Outline files
        outline_abs = converter.to_absolute(outline_rel)

        return ContextGenerator(
            collector,
            settings,
            project_root,
            converter,
            full_rel,
            full_abs,
            outline_rel,
            outline_abs,
        )

    # Generate file context based on provided or stored files
    def files(self, in_files: list[str] = []) -> str:
        rel_paths = in_files if in_files else self.full_rel  # Use provided files or all stored files
        return self._render("files", {"files": self.collector.files(rel_paths)})  # Render the file context

    # Generate full project context including folder structure, outlines, and more
    def context(self) -> str:
        ctx_settings = self.settings.context_config.get_settings()  # Get context settings
        (no_media, with_prompt) = (ctx_settings["no_media"], ctx_settings["with_prompt"])  # Handle settings for media and prompts
        context = {
            "project_name": self.project_root.name,
            "folder_structure_diagram": self.collector.folder_structure_diagram(
                self.full_abs, self.outline_abs, no_media  # Generate folder structure diagram
            ),
            "summary": self.settings.get_summary(),  # Project summary
            "files": self.collector.files(self.full_rel),  # List of files and content
            "highlights": self.collector.outlines(self.outline_rel),  # Highlights from outlines
            "sample_requested_files": self.converter.to_relative(
                self.collector.sample_file_abs(self.full_abs)  # Sample incomplete files
            ),
            "prompt": self.settings.get_prompt() if with_prompt else None,  # Project prompt
        }
        return self._render("context", context)  # Render the context

    # Internal method to render templates using the provided context
    def _render(self, template_id: str, context: dict) -> str:
        template_name = self.settings.context_config.config["templates"][template_id]  # Get template name
        template = Template.create(
            template_name, context, self.settings.project_layout.templates_path  # Create a template instance
        )
        return template.render()  # Render and return the template


# Function to return the file context
def _files(in_files: list[str] = []) -> str:
    if not in_files:
        profile_feedback()  # Provide feedback if no files provided
    return ContextGenerator.create().files(in_files)  # Generate files context


# Function to return the full project context
def _context() -> str:
    profile_feedback()  # Provide feedback
    return ContextGenerator.create().context()  # Generate full context


# Create entry points for different file context generation methods
files_from_scratch = create_entry_point(lambda: _files())  # Generate from scratch
files_from_clip = create_entry_point(lambda: _files(pyperclip.paste().strip().split("\n")))  # Generate from clipboard
context = create_entry_point(_context)  # Generate full context


# Main function to run the script
def main():
    files_from_scratch()  # Generate file context from scratch


# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()

