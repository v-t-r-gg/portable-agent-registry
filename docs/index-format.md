# Index format (schema 0)

`index.json` is owned by this registry. It is not a self-nomad schema.

```json
{
  "index_schema": 0,
  "self_nomad_min": "1.1.0",
  "packages": [
    {
      "name": "demo-echo",
      "self_id": "<uuid>",
      "description": "...",
      "profile": "specialist",
      "pack": "packages/demo-echo/1.0.0/demo-echo.snpack",
      "content_digest": "sha256:<hex>",
      "skills": ["echo"],
      "runtimes_tested": ["hermes", "openclaw"],
      "packer_version": "1.1.0"
    }
  ]
}
```

`content_digest` is the `content_digest` field from `self-nomad pack --check --json`, prefixed with `sha256:`. `skills` is that command's `skills` array. `self_id`, `name`, and `description` come from the sidecar `self` object.

Namespace `author/name` is deferred. One-author seeds use the folder name plus `self_id`.

CI and `scripts/validate_index.py` install self-nomad and compare the index to `pack --check`. They do not reimplement validation.
