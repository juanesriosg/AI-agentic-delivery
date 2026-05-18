# Skill: Screenshot Annotation

Use annotations to make visual feedback actionable.

## Annotation fields

- id
- severity
- screenshot path
- viewport
- box coordinates when available
- expected behavior
- actual behavior
- owner agent
- verification required

## Example

```bash
python .ai/scripts/annotate_screenshot.py \
  --image .agent/stories/STORY-1/screenshots/mobile.png \
  --annotations .agent/stories/STORY-1/annotations/issues.json \
  --out .agent/stories/STORY-1/screenshots/mobile-annotated.png
```
