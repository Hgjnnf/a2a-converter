import click
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .config_schema import CLIConfig

TEMPLATES_DIR = Path(__file__).parent / "templates"

@click.group()
def divy_a2a():
    """Divy A2A: scaffold an A2A-compliant agent server."""
    pass

@divy_a2a.command()
@click.option(
    "--output", "-o",
    default="settings.yaml",
    help="Where to write the stub settings YAML"
)
def init(output):
    """
    Generate a stub settings.yaml for your agent metadata & settings.
    """
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    stub = env.get_template("settings_stub.yaml.j2").render()
    Path(output).write_text(stub)
    click.echo(f"🌱 Created stub configuration at {output}")

@divy_a2a.command()
@click.option(
    "--config", "-c",
    default="settings.yaml",
    help="Path to your filled-out settings YAML"
)
def convert(config):
    """
    Read & validate settings.yaml, then render
    three modules:
      • agent_executor.py
      • task_handler.py
      • a2a_agent_wrapper.py
    """
    # 1. Load & validate YAML
    data = yaml.safe_load(Path(config).read_text())
    conf = CLIConfig(**data)  # raises if invalid

    # 2. Prepare Jinja environment
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # 3. Render mappings: template → output filename
    mapping = {
        "agent_server.py.j2":       "agent_server.py",
        "task_handler.py.j2":       "task_handler.py",
        "a2a_agent_wrapper.py.j2":  "a2a_agent_wrapper.py",
    }

    for tpl, out in mapping.items():
        rendered = env.get_template(tpl).render(**conf.dict())
        Path(out).write_text(rendered)
        click.echo(f"✅ Generated {out}")

if __name__ == "__main__":
    divy_a2a()
