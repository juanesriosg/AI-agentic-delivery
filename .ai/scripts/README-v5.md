# v5 Scripts

Main script:

```bash
python .ai/scripts/agentic_sdlc.py doctor
python .ai/scripts/agentic_sdlc.py scan
python .ai/scripts/agentic_sdlc.py run-once --mode local --max-specs 1
python .ai/scripts/agentic_sdlc.py watch --mode local
python .ai/scripts/agentic_sdlc.py cloud-plan
```

Shell helpers:

```bash
.ai/scripts/start_local_agent_loop.sh
.ai/scripts/prepare_night_cloud_plan.sh
.ai/scripts/run_agentic_once.sh local 1
```

Guardrails:

```bash
python .ai/scripts/pr_guardrails.py --base dev/my-spec --task-id frontend-form
python .ai/scripts/aws_terraform_guardrails.py --base dev/my-spec --task-id lambda-api --aws-change
```
