# Migrate From Dockerfile

You do not have to convert a hand-written Dockerfile into PeiDocker line for line. The faster path is to map intent to the right PeiDocker layer.

## Concept Mapping

| Dockerfile idea | PeiDocker equivalent |
| --- | --- |
| `FROM ubuntu:24.04` | `stage_1.image.base` |
| Base-system `RUN apt install ...` | stage-1 config or stage-1 `custom.on_build` |
| App-layer `RUN ...` | stage-2 `custom.on_build` |
| `ENV KEY=value` | `stage_1.environment` or `stage_2.environment` |
| `EXPOSE 8080` | `stage_1.ports` or `stage_2.ports` |
| `VOLUME /data` | `stage_2.storage` or `stage_2.mount` |
| `ENTRYPOINT` / `CMD` | default entrypoint behavior or `custom.on_entry` |

## Practical Migration Order

1. Move the base image into `stage_1.image.base`.
2. Move stable OS setup into stage-1.
3. Move app-specific setup into stage-2.
4. Replace hardcoded storage paths with `storage:` and `mount:`.
5. Replace monolithic shell `RUN` blocks with custom scripts where that improves clarity.

## What Usually Stays Out Of PeiDocker

- very image-specific Dockerfile tricks unrelated to the PeiDocker runtime model
- custom multi-service orchestration outside the generated compose model
- host-specific hacks better kept in wrapper scripts

## Good First Pairing

- [Two-Stage Architecture](../../manual/concepts/two-stage-architecture.md)
- [Project Structure](../../manual/getting-started/project-structure.md)
- [Storage And Mounts](../../manual/guides/storage-and-mounts.md)
