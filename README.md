# a2a-converter
Make any agents A2A compatible in under a minute!

## How to use:
1. Install our package
    - For now, you can
        - clone the repo
        - run `pip install -e .`
    - pip install will be available soon
2. Run `divy_a2a init` to generate a settings file
3. Fill out the generated `settings.yaml` file with your agent's details
4. Run `divy_a2a convert` to convert your agent to A2A compatible format

Now you can run your A2A compatible agent using `python agent_executor.py`

## Commands

All CLI commands live under the `divy_a2a` group. Run:

```bash
divy_a2a --help
```

to see the full list of available commands.

### init
```bash
divy_a2a init
```

Usage: divy_a2a init [OPTIONS]

- Generate a stub settings.yaml for your agent metadata & settings.

Options:
>  -o, --output TEXT  Where to write the stub settings YAML  [default: settings.yaml] <br>
>  --help             Show this message and exit.

Examples
```bash
# write to the default settings.yaml
divy_a2a init

# write to a custom path
divy_a2a init --output my_agent_settings.yaml
```

### convert
```bash
divy_a2a convert
```

Usage: divy_a2a convert [OPTIONS]

Read & validate settings.yaml, then render:
> - agent_executor.py
> - task_handler.py
> - a2a_agent_wrapper.py
  Also patches requirements.txt and runs pip install.

Options:
>  -c, --config TEXT  Path to your filled-out settings YAML  [default: settings.yaml] <br>
>  --help             Show this message and exit.

Examples
```bash
# convert using the default settings.yaml
divy_a2a convert

# convert using a custom config file
divy_a2a convert --config my_agent_settings.yaml
```

---

Supported Frameworks:
- OpenAI

Work in Progress:
- LangGraph
- CrewAI
