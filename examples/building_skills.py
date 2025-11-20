"""
Example: How to programmatically build and save a new skill.

This script demonstrates the concept of the AI "learning" a skill by saving
a working function to the skills directory.
"""

import inspect
from pathlib import Path


# 1. Define the function we want to save as a skill
# In a real scenario, this might be code the AI generated and verified.
def hello_world_skill(name: str = "World") -> str:
    """
    A simple greeting skill.

    Args:
        name: The name to greet.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}! This skill was generated programmatically."


# 2. Define the code generator
def save_skill(function, filename: str, description: str):
    """
    Saves a python function as a standalone skill file.
    """
    skills_dir = Path("skills")
    skills_dir.mkdir(exist_ok=True)

    filepath = skills_dir / filename

    # Get the source code of the function
    source = inspect.getsource(function)

    # Create the file content
    content = f'''"""
{description}
"""

{source}
'''

    # Write to file
    with open(filepath, "w") as f:
        f.write(content)

    print(f"✓ Skill saved to {filepath}")


# 3. Run the builder
if __name__ == "__main__":
    print("Building 'hello_world' skill...")
    save_skill(hello_world_skill, "hello_world.py", "A demonstrated skill created by examples/building_skills.py")

    print("\nYou can now use it like this:")
    print("from skills.hello_world import hello_world_skill")
    print("print(hello_world_skill('User'))")
