# runtime-gvisor-release

BOSH release providing [gVisor](https://gvisor.dev) (runsc) as a container runtime for Cloud Foundry diego-cells.

## Usage

Colocate on diego-cells alongside garden-runc-release (gVisor fork):

```yaml
instance_groups:
- name: diego-cell-gvisor
  jobs:
  - name: garden
    release: garden-runc  # from vlast3k/garden-runc-release@cf-gvisor-support
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
| `runsc` | [vlast3k/gvisor@cf-garden-gvisor-support](https://github.com/vlast3k/gvisor/tree/cf-garden-gvisor-support) | gVisor sandbox runtime (7 CF patches) |
| `containerd-shim-runsc-v1` | Same repo | containerd shim for runsc |

## Building

```bash
# Build runsc + shim on the EC2 build machine (or any Linux amd64 with Bazel):
cd gvisor
bazel build -c opt //runsc
bazel build -c opt //shim

# Copy to blobstore:
bosh add-blob bazel-bin/runsc/runsc_/runsc runsc/runsc
bosh add-blob bazel-bin/shim/containerd-shim-runsc-v1_/containerd-shim-runsc-v1 shim/containerd-shim-runsc-v1
bosh create-release --force
```

## Requirements

- Garden-runc-release from `vlast3k/garden-runc-release@cf-gvisor-support`
  (contains Guardian with execPeas + loopback patches)
- Ubuntu Jammy stemcell (22.04, kernel 5.15+)
- Isolation segment for gVisor cells

## Architecture

See [Docker on gVisor — how it works](docs/architecture.md) for the full flow.
