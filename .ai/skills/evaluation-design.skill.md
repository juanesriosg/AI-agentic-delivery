# Skill: evaluation-design

## Purpose
Design eval cases that verify whether skill changes improve future agent behavior.

## Operating context
Evals live under `.ai/evals/**` and are run by `.ai/scripts/skill_eval_runner.py`. Some evals are deterministic, some are model-judged, and high-stakes cases require human calibration.

## Principles
- Evals should fail when behavior is wrong.
- Keep holdout cases stable.
- Do not let agents weaken evals just to pass.
- Prefer metrics that correlate with trust and quality.

## Measurement levels
- Output level: Was the patch, review, label, summary, or SQL answer correct and useful?
- Trajectory level: Did the agent inspect the right files, run the right tools, and stop at the right time?
- System level: Did cycle time, merge quality, trust, cost, noise, or rework improve?

## Eval types
- Code-based: parseable outcome or invariant.
- Model-based: judgment rubric.
- Human-calibrated: high-stakes or immature rubric.

## Procedure
1. Define the behavior to improve.
2. Add easy, realistic, and adversarial cases.
3. Define pass/fail criteria.
4. Include at least one holdout case for important skills.
5. Run deterministic evals first.
6. Mark cases requiring human calibration.

## Anti-patterns
- Rewarding comment count.
- Rewarding long answers.
- Allowing evals to be changed just to pass.
- Optimizing for speed when correctness/trust is the objective.

## Quality bar
An eval suite must include easy, realistic, adversarial, and where relevant holdout cases. Each case needs expected behavior and concrete failure conditions.

## Uncertainty behavior
When a rubric is immature or the stakes are high, mark the case as requiring human calibration instead of pretending deterministic checks are enough.

## Feedback hooks
Use failed evals, reviewer disagreement, and calibration notes as feedback for future self-improvement proposals.
