# Contributing

Work locally, keep the core independent of GUI frameworks, and run:

```bash
python3 -m unittest discover -s tests -v
./verify_app.sh
```

Do not add telemetry, mandatory network calls or external API requirements.
