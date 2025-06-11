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

---

Supported Agents:
- OpenAI

Work in Progress:
- LangGraph
- CrewAI
