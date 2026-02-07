# Stage 2 System Scripts

Most scripts under `stage-2/system/**` are **compatibility wrappers** that forward
to canonical implementations under `stage-1/system/**`.

Prefer referencing `stage-1/system/**` paths directly in `user_config.yml`.

Exceptions:

- Some scripts may remain stage-2-only when they genuinely depend on stage-2
  runtime storage mechanics (e.g., certain `conda/auto-install-*` flows).
