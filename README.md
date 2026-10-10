# runtime-gvisor-release

BOSH release providing [gVisor](https://gvisor.dev) (runsc) as a container runtime for Cloud Foundry diego-cells.

## Usage

Colocate on diego-cells alongside garden-runc-release (gVisor fork):

```yaml
instance_groups:
- name: diego-cell-gvisor
  jobs:
  - name: garden
    release: garden-runc  # cleanup7-enabled alternative-runtime release
    properties:
      garden:
        containerd_runtime_type: io.containerd.runsc.v1
  - name: rep
    release: diego
    properties:
      diego:
        rep:
          placement_tags: ["gvisor"]
          enable_container_proxy: true
  - name: gvisor-runtime
    release: runtime-gvisor
    properties:
      gvisor:
        overlay2: "none"    # required for Garden StreamIn visibility
        network: "sandbox"  # gVisor's userspace netstack
        debug: false
```

## Components

| Binary | Source | Purpose |
|--------|--------|---------|
| `runsc` | [vlast3k/gvisor@0e57dfe144cb](https://github.com/vlast3k/gvisor/commit/0e57dfe144cba0fef36adb4511fa54a1c4d71475) | gVisor sandbox runtime with CF V1, V2, and V4 only |
| `containerd-shim-runsc-v1` | Same source revision, stock binary | containerd shim for runsc |
| `gvisor_sentry` | Same source revision, stock binary | Release-matched external Sentry for strict sidecar mode |

The source branch is `cfar-1501-release-20261005-stock`, based on official
gVisor `release-20261005.0`. Exact artifact sizes and hashes are recorded in
`ARTIFACTS.json` and checked by `scripts/verify_artifacts.py`.

## Building

```bash
# Build all runtime artifacts on Linux amd64 with Bazel 8.3.1:
cd gvisor
bazel build --config=x86_64 \
  //runsc:runsc \
  //shim:containerd-shim-runsc-v1 \
  //runsc/cmd/sentry:gvisor_sentry

# Copy to blobstore:
bosh add-blob bazel-bin/runsc/runsc_/runsc runsc/runsc
bosh add-blob bazel-bin/shim/containerd-shim-runsc-v1_/containerd-shim-runsc-v1 shim/containerd-shim-runsc-v1
bosh add-blob bazel-bin/runsc/cmd/sentry/gvisor_sentry_/gvisor_sentry sentry/gvisor_sentry

python3 scripts/verify_artifacts.py
bosh create-release --force --version 0.2.0-cfar1502 \
  --tarball /tmp/runtime-gvisor-release-20261005-v1-v2-v4.tgz
```

## Requirements

- A cleanup7-enabled Garden-runc release with Guardian alternative-runtime support
- Ubuntu Jammy stemcell (22.04, kernel 5.15+)
- Isolation segment for gVisor cells

## Architecture

See [Docker on gVisor — how it works](docs/architecture.md) for the full flow.
