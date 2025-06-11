import click
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .config_schema import CLIConfig

TEMPLATES_DIR       = Path(__file__).parent / "templates"
COMMON_TPL_DIR      = TEMPLATES_DIR / "common"
FRAMEWORKS_TPL_ROOT = TEMPLATES_DIR / "frameworks"
SUPPORTED = {"langgraph", "openai", "crewai"}

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
@click.option("--config", "-c", default="settings.yaml")
def convert(config):
    # 1. Load & validate YAML
    data = yaml.safe_load(Path(config).read_text())
    conf = CLIConfig(**data)

    # 2. Determine framework (default to openai)
    framework = getattr(conf, "framework", None).value or "openai"
    if framework not in SUPPORTED:
        raise click.ClickException(f"Unsupported framework: {framework!r}. "
                                   f"Choose one of {sorted(SUPPORTED)}")

    # 3. Build a loader that first looks in the framework folder, then base
    framework_dir = FRAMEWORKS_TPL_ROOT / framework
    loader = FileSystemLoader([
        str(framework_dir),
        str(COMMON_TPL_DIR),
    ])
    env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    mapping = {
        "agent_executor.py.j2":      "agent_executor.py",
        "task_handler.py.j2":        "task_handler.py",
        "a2a_agent_wrapper.py.j2":   "a2a_agent_wrapper.py",
    }

    for tpl_name, out_name in mapping.items():
        tpl = env.get_template(tpl_name)
        rendered = tpl.render(**conf.dict())
        Path(out_name).write_text(rendered)
        click.echo(f"✅ Generated {out_name}")

if __name__ == "__main__":
    divy_a2a()
