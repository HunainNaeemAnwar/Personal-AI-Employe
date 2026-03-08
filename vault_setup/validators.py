"""Validators for task files and YAML frontmatter.

This module provides validation functions for task files created by watchers
and ensures they conform to the task-file-schema.json specification.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

import yaml


def validate_yaml_frontmatter(content: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Validate YAML frontmatter in a markdown file.

    Args:
        content: Full markdown file content

    Returns:
        Tuple of (is_valid, error_message, frontmatter_dict)
    """
    # Check if content starts with --- (YAML frontmatter delimiter)
    if not content.startswith("---"):
        return False, "File must start with YAML frontmatter (---)", {}

    # Split content by --- delimiter (limit to 2 splits to get: empty, frontmatter, body)
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False, "Invalid YAML frontmatter format (missing closing ---)", {}

    # Parse YAML from the middle section (parts[1])
    try:
        frontmatter = yaml.safe_load(parts[1])
        # Ensure frontmatter is a dictionary, not a string or list
        if not isinstance(frontmatter, dict):
            return False, "YAML frontmatter must be a dictionary", {}
        return True, "", frontmatter
    except yaml.YAMLError as e:
        return False, f"Invalid YAML syntax: {e}", {}


def validate_task_file(file_path: Path) -> Tuple[bool, str]:
    """Validate a task file against the task-file-schema.json specification.

    Args:
        file_path: Path to the task file

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file exists
    if not file_path.exists():
        return False, f"File does not exist: {file_path}"

    # Read file content
    try:
        content = file_path.read_text()
    except Exception as e:
        return False, f"Error reading file: {e}"

    # Validate YAML frontmatter
    is_valid, error_msg, frontmatter = validate_yaml_frontmatter(content)
    if not is_valid:
        return False, error_msg

    # Check required fields
    required_fields = ["type", "source", "timestamp", "priority", "status"]
    for field in required_fields:
        if field not in frontmatter:
            return False, f"Missing required field: {field}"

    # Validate field values
    valid_types = ["email", "file_drop", "transaction"]
    if frontmatter["type"] not in valid_types:
        return False, f"Invalid type: {frontmatter['type']}. Must be one of {valid_types}"

    valid_priorities = ["high", "medium", "low"]
    if frontmatter["priority"] not in valid_priorities:
        return (
            False,
            f"Invalid priority: {frontmatter['priority']}. Must be one of {valid_priorities}",
        )

    valid_statuses = ["pending", "in_progress", "completed"]
    if frontmatter["status"] not in valid_statuses:
        return (
            False,
            f"Invalid status: {frontmatter['status']}. Must be one of {valid_statuses}",
        )

    # Validate timestamp format (ISO 8601)
    # Replace 'Z' with '+00:00' for Python's fromisoformat() compatibility
    try:
        datetime.fromisoformat(frontmatter["timestamp"].replace("Z", "+00:00"))
    except (ValueError, AttributeError) as e:
        return False, f"Invalid timestamp format: {frontmatter['timestamp']}. Must be ISO 8601"

    # Validate source is non-empty
    if not frontmatter["source"] or not isinstance(frontmatter["source"], str):
        return False, "Source must be a non-empty string"

    return True, ""


def validate_skill(skill_path: Path) -> Tuple[bool, str]:
    """Validate an Agent Skill SKILL.md file.

    Args:
        skill_path: Path to the skill directory (containing SKILL.md)

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check skill directory exists
    if not skill_path.exists():
        return False, f"Skill directory does not exist: {skill_path}"

    if not skill_path.is_dir():
        return False, f"Skill path is not a directory: {skill_path}"

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, f"SKILL.md not found in {skill_path}"

    # Read SKILL.md content
    try:
        content = skill_md.read_text()
    except Exception as e:
        return False, f"Error reading SKILL.md: {e}"

    # Validate YAML frontmatter
    is_valid, error_msg, frontmatter = validate_yaml_frontmatter(content)
    if not is_valid:
        return False, error_msg

    # Check required frontmatter fields
    if "name" not in frontmatter:
        return False, "Missing required field in frontmatter: name"

    if "description" not in frontmatter:
        return False, "Missing required field in frontmatter: description"

    # Validate name format
    name = frontmatter["name"]
    if not isinstance(name, str):
        return False, "Skill name must be a string"

    # Name must be lowercase alphanumeric with hyphens only (e.g., "email-triage")
    if not re.match(r"^[a-z0-9-]+$", name):
        return False, f"Invalid skill name format: {name}. Must be lowercase with hyphens only"

    # Enforce maximum length for filesystem compatibility
    if len(name) > 64:
        return False, f"Skill name too long: {len(name)} chars. Maximum 64 characters"

    # Check for reserved words
    reserved_words = ["anthropic", "claude"]
    if name in reserved_words:
        return False, f"Skill name cannot be a reserved word: {name}"

    # Validate description
    description = frontmatter["description"]
    if not isinstance(description, str):
        return False, "Skill description must be a string"

    if len(description) > 1024:
        return False, f"Description too long: {len(description)} chars. Maximum 1024 characters"

    if not description.strip():
        return False, "Description cannot be empty"

    # Check for required sections in body (after frontmatter)
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False, "Invalid SKILL.md format"

    body = parts[2]  # Everything after the closing ---

    # Check for Instructions section
    if "## Instructions" not in body:
        return False, "Missing required section: ## Instructions"

    # Check for Examples section
    if "## Examples" not in body:
        return False, "Missing required section: ## Examples"

    # Validate sections have content (not just headers)
    # Regex captures content between "## Instructions" and next "##" or end of file
    instructions_match = re.search(r"## Instructions\s*\n(.+?)(?=\n##|\Z)", body, re.DOTALL)
    if not instructions_match or not instructions_match.group(1).strip():
        return False, "Instructions section is empty"

    # Same for Examples section
    examples_match = re.search(r"## Examples\s*\n(.+?)(?=\n##|\Z)", body, re.DOTALL)
    if not examples_match or not examples_match.group(1).strip():
        return False, "Examples section is empty"

    return True, ""


def generate_task_filename(
    task_type: str, subject: str, timestamp: datetime = None
) -> str:
    """Generate a standardized task filename.

    Args:
        task_type: Type of task (email, file_drop, transaction)
        subject: Subject or description for the task
        timestamp: Optional timestamp (defaults to current UTC time)

    Returns:
        Generated filename in format: {TYPE}_{TIMESTAMP}_{SLUG}.md
    """
    if timestamp is None:
        timestamp = datetime.utcnow()

    # Convert type to uppercase
    type_prefix = task_type.upper()

    # Generate timestamp string
    timestamp_str = timestamp.strftime("%Y%m%dT%H%M%S") + "Z"

    # Slugify subject
    slug = slugify(subject)

    return f"{type_prefix}_{timestamp_str}_{slug}.md"


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to URL-safe slug.

    Args:
        text: Text to slugify
        max_length: Maximum length of slug (default: 50)

    Returns:
        Slugified text
    """
    # Convert to lowercase for consistency
    text = text.lower()

    # Remove non-alphanumeric characters (except spaces and hyphens)
    # \w matches [a-zA-Z0-9_], \s matches whitespace
    text = re.sub(r"[^\w\s-]", "", text)

    # Replace spaces and multiple consecutive hyphens with single hyphen
    text = re.sub(r"[-\s]+", "-", text)

    # Remove leading/trailing hyphens (e.g., "-test-" becomes "test")
    text = text.strip("-")

    # Truncate to max_length for filesystem compatibility
    return text[:max_length]


def validate_task_file_batch(directory: Path) -> Dict[str, Tuple[bool, str]]:
    """Validate all task files in a directory.

    Args:
        directory: Path to directory containing task files

    Returns:
        Dictionary mapping filename to (is_valid, error_message)
    """
    results = {}

    if not directory.exists() or not directory.is_dir():
        return results

    for file_path in directory.glob("*.md"):
        is_valid, error_msg = validate_task_file(file_path)
        results[file_path.name] = (is_valid, error_msg)

    return results


def get_validation_summary(results: Dict[str, Tuple[bool, str]]) -> Dict[str, Any]:
    """Generate a summary of validation results.

    Args:
        results: Dictionary from validate_task_file_batch()

    Returns:
        Summary dictionary with counts and details
    """
    total = len(results)
    valid = sum(1 for is_valid, _ in results.values() if is_valid)
    invalid = total - valid

    invalid_files = {
        filename: error_msg for filename, (is_valid, error_msg) in results.items() if not is_valid
    }

    return {
        "total": total,
        "valid": valid,
        "invalid": invalid,
        "invalid_files": invalid_files,
    }
