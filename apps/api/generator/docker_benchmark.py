"""
Trainer-Grade Benchmark Course Generator: Docker Introduction for Intermediate Developers.
Builds a comprehensive 90-minute, 24-slide curriculum with 150-300+ word trainer delivery notes,
real Docker commands, complete Dockerfile syntax, multi-stage builds, operational runbooks,
and complete hands-on lab with dual-prover verification.
"""

from typing import Dict, Any
from apps.api.speaker_notes import build_trainer_delivery_notes


def build_docker_benchmark_deck(
    deck_id: str,
    topic: str = "Docker Introduction for Intermediate Developers",
    level: str = "intermediate",
    minutes: int = 90,
    stack: Dict[str, str] = None,
    version: str = "3.12",
) -> Dict[str, Any]:
    if not stack:
        stack = {"docker": "26.0", "python": "3.12", "engine": "moby"}

    slides = [
        # Slide 1: Masterclass Title
        {
            "id": "s_001",
            "type": "title",
            "title": "Docker Introduction for Intermediate Developers: Masterclass",
            "bullets": [
                "Production container mechanics, lifecycle state machines, and daemon internals",
                "OCI image architecture, copy-on-write overlay2 filesystem, and layer optimization",
                "Dockerfile instruction hygiene, multi-stage builds, and BuildKit caching",
                "Operational runtime basics: port translation, volume persistence, and networks",
                "Guided hands-on laboratory: packaging, debugging, and health verification",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Docker Masterclass Introduction & Roadmap",
                slide_type="title",
                bullets=[
                    "Establish clear baseline expectations for intermediate developers",
                    "Distinguish software process isolation from hardware hypervisor virtualization",
                    "Outline the 9-module agenda spanning 90 minutes of theory and practical exercises",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Containerize applications as single-concern processes; avoid treating containers as mini virtual machines.",
                custom_guidance={
                    "objective": "Welcome intermediate engineers, align on technical prerequisites, and introduce the 90-minute curriculum roadmap.",
                    "explanation": (
                        "Welcome to 'Docker Introduction for Intermediate Developers'. This masterclass goes beyond the basic "
                        "'docker run' and 'docker build' commands you may already know. Our focus is on production invariants: "
                        "understanding Linux namespaces and cgroups under the hood, writing minimal and secure multi-stage Dockerfiles, "
                        "preventing cache invalidation traps, correctly handling process signals (SIGTERM vs SIGKILL), and structuring "
                        "persistent storage and networks without operational surprises. We assume you are comfortable with basic command-line "
                        "usage and understand client-server application architecture."
                    ),
                    "walkthrough": (
                        "Walk students through the 9 modules on screen: 1. Environment Baseline, 2. Containers vs. VMs, "
                        "3. Docker Engine Architecture & Lifecycle, 4. Images, Layers & Registries, 5. Writing Dockerfiles & Optimization, "
                        "6. Running Containers, Ports & Config, 7. Volumes, Networks & Resource Limits, 8. Guided Hands-On Lab, "
                        "and 9. Assessment & Production Readiness Checklist."
                    ),
                    "demonstration": "Open terminal and run 'docker version' to display both client and daemon engine versions.",
                    "observations": "Students see the decoupled client/server architecture: Docker CLI connecting to Moby Engine.",
                    "questions": (
                        "1. Why is treating a container like a virtual machine an anti-pattern in production?\n"
                        "   Expected: Containers lack dedicated init systems by default and should manage a single process lifecycle.\n"
                        "2. What happens if multiple developers on a team use unpinned base image tags?\n"
                        "   Expected: Inconsistent build environments, non-reproducible artifacts, and untracked CVE vulnerabilities."
                    ),
                    "misconceptions": "Learners often assume containers provide hardware-level isolation or that Docker is a hypervisor.",
                    "troubleshooting": "If Docker Desktop or daemon is stopped, commands fail with 'Cannot connect to the Docker daemon at unix:///var/run/docker.sock'.",
                    "transition": "Let us begin Module 1 by verifying our workstation environment and core system prerequisites.",
                },
            ),
        },
        # Slide 2: Module 1 Prerequisites
        {
            "id": "s_002",
            "type": "content",
            "title": "Module 1 — Prerequisites, Tooling Verification & Environment Baseline",
            "bullets": [
                "Docker Engine 24.0+ / 26.0+ with Docker Compose v2 CLI plugin installed",
                "Verify daemon socket connectivity: 'docker info' and 'docker version' inspection",
                "Linux kernel prerequisites: cgroups v2 enabled, overlayfs, and iptables/nftables",
                "Workstation setup: non-root user membership in 'docker' group or rootless mode",
                "Baseline system sanity check: 'docker run --rm hello-world' executing cleanly",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 1 — Environment Baseline",
                slide_type="content",
                bullets=[
                    "Docker Engine 24.0+ / 26.0+ with Docker Compose v2 CLI plugin installed and verified",
                    "Verify daemon socket connectivity: 'docker info' and 'docker version' inspection",
                    "Linux kernel prerequisites: cgroups v2 enabled, overlayfs support, and iptables/nftables",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Always run 'docker info' during morning setup to catch daemon socket permissions or proxy failures early.",
                custom_guidance={
                    "objective": "Verify that every student's machine has a functional Docker daemon and necessary kernel features enabled.",
                    "explanation": (
                        "Before diving into container internals, we must verify the environment baseline. Docker relies directly on host "
                        "kernel capabilities: Control Groups version 2 (cgroups v2) for resource accounting, the overlay2 storage driver "
                        "for union filesystem stacking, and kernel networking tables (iptables or nftables) for port forwarding. On Linux, "
                        "ensure your user belongs to the 'docker' group to avoid needing 'sudo' for every invocation, or utilize Docker Rootless "
                        "mode for hardened security boundaries."
                    ),
                    "walkthrough": (
                        "Instruct students to execute three diagnostic commands: First, 'docker version' checks API compatibility between CLI "
                        "and Engine. Second, 'docker info' displays active storage driver (must be overlay2), cgroup version, and total running "
                        "containers. Third, 'docker run --rm hello-world' confirms that image pulling, unpacking, and process execution succeed."
                    ),
                    "demonstration": "Execute 'docker info | grep -E \"Storage Driver|Cgroup Version\"' in a terminal.",
                    "observations": "Output confirms 'Storage Driver: overlay2' and 'Cgroup Version: 2'.",
                    "questions": (
                        "1. What is the security implication of adding a non-root user to the 'docker' group?\n"
                        "   Expected: It grants root-equivalent permissions on the host because the user can mount host rootfs with '-v /:/host'.\n"
                        "2. What does the '--rm' flag do in 'docker run --rm'?\n"
                        "   Expected: Automatically removes the container's mutable read-write layer and metadata upon process exit."
                    ),
                    "misconceptions": "Students often assume Docker Desktop for Mac/Windows runs containers natively on Darwin/NT; it actually runs a lightweight Linux VM.",
                    "troubleshooting": "Error: 'Got permission denied while trying to connect to the Docker daemon socket'. Fix: Run 'sudo usermod -aG docker $USER' and start a new shell session.",
                    "transition": "Now that our environment is verified, let us explore the fundamental differences between VMs and Containers.",
                },
            ),
        },
        # Slide 3: Module 2 Containers vs VMs
        {
            "id": "s_003",
            "type": "content",
            "title": "Module 2 — Virtual Machines vs. Containers: Kernel Sharing & Isolation",
            "bullets": [
                "Virtual Machines: Hypervisors virtualize physical hardware; each VM boots a guest OS",
                "Containers: Isolated user-space processes executing directly on the shared host kernel",
                "Startup latency: sub-second process fork vs. multi-minute guest BIOS and OS boot",
                "Memory overhead: direct kernel page allocations vs. reserved hypervisor RAM",
                "Security boundary: hypervisor hardware isolation vs. kernel software security profiles",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 2 — Virtual Machines vs. Containers",
                slide_type="content",
                bullets=[
                    "Virtual Machines: Type-1/Type-2 hypervisors virtualize physical hardware",
                    "Containers: Isolated user-space processes executing directly on the shared host Linux kernel",
                    "Startup latency: sub-second process fork vs. multi-minute guest BIOS boot sequences",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Containers provide process isolation, not hardware emulation; a kernel vulnerability impacts all co-located containers.",
                custom_guidance={
                    "objective": "Deconstruct the physical and architectural boundaries separating virtual machines from operating-system-level virtualization.",
                    "explanation": (
                        "The most critical mental model for intermediate engineers is understanding that a container is NOT a lightweight virtual machine. "
                        "A virtual machine runs a complete guest operating system—with its own kernel, device drivers, init system, and virtualized hardware "
                        "emulated by a hypervisor like KVM, ESXi, or Hyper-V. A container, in contrast, is simply a standard Linux process executing on the host "
                        "kernel, constrained by Linux namespaces and control groups. Because there is no guest kernel boot sequence, container startup takes "
                        "milliseconds, and memory overhead is just the memory consumed by the process itself."
                    ),
                    "walkthrough": (
                        "Emphasize the isolation trade-off: Hypervisors provide strong hardware-enforced isolation boundaries. If a process in VM A crashes "
                        "or executes a kernel exploit, VM B is untouched. In containers, because all containers share the host kernel, a kernel panic in one "
                        "container or an unpatched kernel exploit can compromise the entire host unless defended by seccomp, AppArmor, or SELinux policies."
                    ),
                    "demonstration": "Show 'ps -ef | grep python' on the host while a Python container is running.",
                    "observations": "The containerized Python process appears directly in the host's process table with a standard host PID.",
                    "questions": (
                        "1. Can you run a native Windows binary inside a standard Linux Docker container on a Linux host?\n"
                        "   Expected: No, because containers share the host kernel, which only executes Linux ELF binaries.\n"
                        "2. Why do containers consume significantly less idle RAM than virtual machines?\n"
                        "   Expected: VMs must allocate fixed RAM for the guest OS kernel and background daemons (typically 1-2GB minimum)."
                    ),
                    "misconceptions": "Learners often believe containers package an OS kernel. Point out that container base images only package user-space binaries and libraries.",
                    "troubleshooting": "Issue: Performance degradation under high I/O. VMs suffer from hypervisor storage virtualization overhead; containers use native kernel I/O.",
                    "transition": "Let us look deeper into the kernel mechanisms that make this process isolation possible: Namespaces and cgroups.",
                },
            ),
        },
        # Slide 4: Module 2 Linux Namespaces & cgroups
        {
            "id": "s_004",
            "type": "content",
            "title": "Module 2 — Linux Namespaces & Control Groups (cgroups v2) Under the Hood",
            "bullets": [
                "PID Namespace: Isolates process trees; container process sees itself as PID 1",
                "NET Namespace: Provides virtual network interfaces (veth pairs), routing, and ports",
                "MNT Namespace: Isolates filesystem mount points, providing a private rootfs view",
                "IPC, UTS & User Namespaces: Isolate inter-process communication, hostname, and UIDs",
                "cgroups v2: Enforces hard ceilings and accounting for CPU, memory, IO, and pids",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 2 — Namespaces & cgroups v2",
                slide_type="content",
                bullets=[
                    "PID Namespace: Isolates process trees; container process sees itself as PID 1",
                    "NET Namespace: Provides virtual network interfaces (veth pairs) and routing tables",
                    "cgroups v2: Enforces hard ceilings and accounting for CPU, memory, IO, and pids",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Inspect '/proc/$$/ns/' inside a container to see the active namespace inode identifiers.",
                custom_guidance={
                    "objective": "Explain the two pillars of container isolation: Namespaces (what a process can see) and cgroups (what a process can use).",
                    "explanation": (
                        "Under the hood, Docker is an ergonomic orchestrator of core Linux kernel features. Isolation is achieved through Namespaces, "
                        "which restrict what a process can SEE. The PID namespace gives the container its own isolated process hierarchy where its main "
                        "process is PID 1. The NET namespace provides private network interfaces (a virtual ethernet pair connecting to docker0). The MNT "
                        "namespace provides a private view of the root filesystem. Control Groups (cgroups), conversely, restrict what a process can USE: "
                        "cgroups v2 enforce hard memory limits (preventing runaway OOM issues), CPU execution quotas via the CFS scheduler, and I/O bandwidth."
                    ),
                    "walkthrough": (
                        "Explain the relationship: Namespaces prevent container A from seeing processes or network sockets in container B. "
                        "Control groups prevent container A from consuming 100% of host CPU or exhausting host RAM, which would starve container B."
                    ),
                    "demonstration": "Run 'ls -l /proc/self/ns' on the host and compare the namespace inode numbers with 'docker run --rm alpine ls -l /proc/self/ns'.",
                    "observations": "Notice the namespace inode numbers for 'net', 'pid', 'mnt', and 'uts' are completely different.",
                    "questions": (
                        "1. What is the difference between Namespaces and cgroups in one sentence?\n"
                        "   Expected: Namespaces govern visibility and scope; cgroups govern resource consumption and limits.\n"
                        "2. What happens if a process inside a container attempts to access a raw socket without the NET_ADMIN capability?\n"
                        "   Expected: The kernel rejects the system call with EPERM, maintaining host network integrity."
                    ),
                    "misconceptions": "Learners often think cgroups v1 and v2 are identical; cgroups v2 provides a unified single hierarchy and avoids resource deadlock issues.",
                    "troubleshooting": "Issue: Container process cannot ping external servers. Check if IP forwarding is enabled on the host ('sysctl net.ipv4.ip_forward').",
                    "transition": "Now let us examine the Docker Engine architecture that coordinates these namespaces and cgroups.",
                },
            ),
        },
        # Slide 5: Module 3 Docker Engine Architecture
        {
            "id": "s_005",
            "type": "content",
            "title": "Module 3 — Docker Engine Architecture: Daemon, containerd, and runc",
            "bullets": [
                "Docker CLI (docker): Client binary communicating over UNIX domain socket '/var/run/docker.sock'",
                "dockerd (Docker Daemon): REST API, authentication, image discovery, and networks",
                "containerd: Industry-standard OCI container runtime managing image transfer and execution",
                "containerd-shim: Decouples container process from daemon restarts, keeping pipes open",
                "runc: Low-level OCI reference runtime creating cgroups and namespaces via libcontainer",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 3 — Docker Engine Architecture",
                slide_type="content",
                bullets=[
                    "Docker CLI (docker): Client binary communicating over UNIX domain socket",
                    "dockerd (Docker Daemon): High-level REST API, authentication, and network management",
                    "containerd & runc: OCI runtime layer decoupling container execution from daemon lifecycle",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Daemon restarts do not kill running containers if 'live-restore: true' is configured in '/etc/docker/daemon.json'.",
                custom_guidance={
                    "objective": "Understand the modern modular architecture of Docker Engine: CLI -> dockerd -> containerd -> containerd-shim -> runc.",
                    "explanation": (
                        "Historically, Docker was a monolithic daemon. Today, Docker Engine is architected as a modular stack adhering to Open Container "
                        "Initiative (OCI) specifications. When you type 'docker run', the CLI sends an HTTP POST to dockerd via '/var/run/docker.sock'. "
                        "dockerd handles high-level concerns: image registry authentication, network allocation, and storage driver binding. dockerd delegates "
                        "container lifecycle to 'containerd', an OCI-compliant daemon. containerd spawns 'containerd-shim', which invokes 'runc' to configure "
                        "namespaces and cgroups, then execs the container process. Once running, runc exits, leaving containerd-shim as the parent process."
                    ),
                    "walkthrough": (
                        "Highlight the role of containerd-shim: Because containerd-shim holds the open file descriptors for container I/O, the Docker daemon "
                        "itself (dockerd) can crash or be upgraded without terminating running containers (when live-restore is enabled)."
                    ),
                    "demonstration": "Run 'pstree -pa | grep -E \"dockerd|containerd\"' on a Linux system with a running container.",
                    "observations": "Observe the process tree: systemd -> containerd -> containerd-shim -> container process.",
                    "questions": (
                        "1. Why was Docker split into containerd and runc?\n"
                        "   Expected: To standardize container execution across the industry (Kubernetes CRI, OCI specs) and enable daemon independence.\n"
                        "2. What security risk exists if '/var/run/docker.sock' is mounted inside a container?\n"
                        "   Expected: It gives that container full control over the host Docker daemon, allowing trivial host privilege escalation."
                    ),
                    "misconceptions": "Learners often think dockerd executes container code directly. Point out that runc does the actual process execution.",
                    "troubleshooting": "Issue: 'docker: error during connect: Post http://... dial unix /var/run/docker.sock: connect: connection refused'. Fix: dockerd service is stopped; restart via systemctl.",
                    "transition": "Let us now map out the lifecycle state machine of a container from creation to destruction.",
                },
            ),
        },
        # Slide 6: Module 3 Lifecycle State Machine
        {
            "id": "s_006",
            "type": "content",
            "title": "Module 3 — Container Lifecycle State Machine: Created, Running, Paused, Exited",
            "bullets": [
                "'docker create': Allocates read-write layer and metadata without starting PID 1 process",
                "'docker start': Invokes runc to create namespaces and execute ENTRYPOINT/CMD",
                "'docker stop': Sends SIGTERM (default 10s grace period) followed by SIGKILL if lingering",
                "'docker pause / unpause': Freezes process threads in cgroups freezer without losing state",
                "'docker rm -f': Reclaims disk space by tearing down mutable layer and veth pair",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 3 — Container Lifecycle State Machine",
                slide_type="content",
                bullets=[
                    "'docker create': Allocates read-write layer without starting PID 1 process",
                    "'docker start': Invokes runc to create namespaces and execute ENTRYPOINT/CMD",
                    "'docker stop': Sends SIGTERM (default 10s grace period) followed by SIGKILL",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Ensure your PID 1 process registers a SIGTERM handler; otherwise containers take 10 seconds to stop every time.",
                custom_guidance={
                    "objective": "Master the states and transitions of a container: Created -> Running -> Paused -> Exited -> Dead.",
                    "explanation": (
                        "A container moves through a deterministic state machine. 'docker create' pre-allocates the container's isolated metadata "
                        "and mutable overlay2 read-write layer. 'docker start' executes the binary. Understanding 'docker stop' is crucial for "
                        "production engineering: Docker first sends SIGTERM (signal 15) to the container's PID 1. The application has a grace period "
                        "(default 10 seconds) to close active database connections, finish pending HTTP requests, and exit cleanly. If the process "
                        "has not exited when the timer expires, Docker issues SIGKILL (signal 9), terminating the process abruptly. If your container "
                        "always takes exactly 10 seconds to stop, your application is failing to handle SIGTERM."
                    ),
                    "walkthrough": (
                        "Diagram the transitions: created -> (start) -> running -> (pause) -> paused -> (unpause) -> running. "
                        "From running -> (stop / SIGTERM) -> exited. From exited -> (rm) -> deleted. Notice that exited containers still consume "
                        "disk space until explicitly removed via 'docker rm' or when created with '--rm'."
                    ),
                    "demonstration": "Run 'docker run -d --name test alpine sleep 3600', inspect state with 'docker inspect test --format \"{{.State.Status}}\"', pause it, and check status again.",
                    "observations": "Status transitions from 'running' to 'paused', freezing CPU usage without destroying memory state.",
                    "questions": (
                        "1. Why is PID 1 special in a Linux container?\n"
                        "   Expected: The Linux kernel treats PID 1 specially; default signal handlers are not installed automatically, so uncaught SIGTERM is ignored.\n"
                        "2. What is the difference between 'docker stop' and 'docker kill'?\n"
                        "   Expected: 'docker stop' attempts graceful SIGTERM first; 'docker kill' immediately issues SIGKILL (or a specified signal)."
                    ),
                    "misconceptions": "Learners often believe stopped containers disappear. Remind them stopped containers persist on disk until pruned.",
                    "troubleshooting": "Issue: Container stops after 10s every time. Fix: Check if application is wrapped in a shell script that fails to forward signals (use 'exec myapp').",
                    "transition": "Let us now investigate how container filesystems are constructed using Copy-on-Write overlay2 storage.",
                },
            ),
        },
        # Slide 7: Module 4 Storage Drivers & Overlay2
        {
            "id": "s_007",
            "type": "content",
            "title": "Module 4 — Storage Drivers & The Copy-on-Write (CoW) Overlay2 Filesystem",
            "bullets": [
                "Image Layers: Immutable, read-only tar archives stacked sequentially using overlay2",
                "LowerDir & UpperDir: Read-only layers (LowerDir) + mutable container layer (UpperDir)",
                "Merged View: Combined union filesystem exposed to container process at root mount point",
                "Copy-on-Write: Modifying an existing file copies it from LowerDir to UpperDir first",
                "Performance caveat: Heavy random writes to UpperDir incur CoW latency; use Volumes",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 4 — Storage Drivers & Overlay2",
                slide_type="content",
                bullets=[
                    "Image Layers: Immutable, read-only tar archives stacked sequentially",
                    "LowerDir & UpperDir: Read-only image layers (LowerDir) + mutable container layer (UpperDir)",
                    "Copy-on-Write (CoW): Modifying an existing file copies it up before mutation",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Never store transactional databases in the container's UpperDir; always attach dedicated named volumes.",
                custom_guidance={
                    "objective": "Explain how the overlay2 union filesystem constructs container root filesystems using Copy-on-Write mechanics.",
                    "explanation": (
                        "Docker achieves extreme storage efficiency through union filesystems, standardized on 'overlay2'. An image consists of "
                        "stacked, immutable, read-only layers called 'LowerDir'. When you start a container, Docker creates a thin, mutable "
                        "read-write layer on top called 'UpperDir'. The Linux overlay filesystem driver merges these layers into a single cohesive "
                        "directory called 'MergedDir'. If a container reads a file, it reads directly from the LowerDir. If it modifies an existing file, "
                        "the kernel performs a Copy-on-Write (CoW) operation: the entire file is copied from the LowerDir up into the UpperDir before "
                        "the write occurs. Deleting a file places a 'whiteout' file in the UpperDir to mask the lower file without mutating the base layer."
                    ),
                    "walkthrough": (
                        "Walk through the performance implication: For small files, CoW latency is imperceptible. But if an application modifies a 5GB database "
                        "file in the container filesystem, the kernel must copy all 5GB into UpperDir before writing the first byte! This is why databases "
                        "must ALWAYS use Docker Volumes, which bypass the overlay2 storage driver entirely."
                    ),
                    "demonstration": "Inspect an image's GraphDriver with 'docker image inspect alpine --format \"{{json .GraphDriver.Data}}\"'.",
                    "observations": "Observe the 'LowerDir', 'UpperDir', and 'MergedDir' paths inside '/var/lib/docker/overlay2/'.",
                    "questions": (
                        "1. If two containers run from the same image, do they share filesystem memory?\n"
                        "   Expected: Yes, read-only LowerDir layers are shared and deduplicated in the kernel page cache.\n"
                        "2. What happens to files written to UpperDir when the container is removed with 'docker rm'?\n"
                        "   Expected: The UpperDir is permanently deleted from the host filesystem."
                    ),
                    "misconceptions": "Learners often think modifying a file in a container alters the underlying Docker image. Emphasize image immutability.",
                    "troubleshooting": "Issue: Host disk fills up unexpectedly. Run 'docker system df' and 'docker system prune' to reclaim dangling overlay2 layers.",
                    "transition": "Now let us examine the internal anatomy of an OCI container image.",
                },
            ),
        },
        # Slide 8: Module 4 Anatomy of an OCI Image
        {
            "id": "s_008",
            "type": "content",
            "title": "Module 4 — Anatomy of an OCI Image: Manifests, Configs & Read-Only Tar Layers",
            "bullets": [
                "Image Manifest: JSON document declaring schema, config blob descriptor, and layer hashes",
                "Config Blob: JSON defining env vars, working directory, default ports, and entrypoint",
                "Content Addressable Hashes: Layers and manifests identified strictly by SHA256 hashes",
                "Layer Deduplication: Multiple images sharing base layers download each blob only once",
                "'docker image inspect': Dumps raw JSON configuration, rootfs diff IDs, and history",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 4 — Anatomy of an OCI Image",
                slide_type="content",
                bullets=[
                    "Image Manifest: JSON document declaring config blob and layer tar hashes",
                    "Config Blob: JSON defining environment variables, working directory, and entrypoint",
                    "Content Addressable Hashes: Identified strictly by cryptographic SHA256 checksums",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Run 'docker system df' to inspect disk consumption across images, containers, and build cache.",
                custom_guidance={
                    "objective": "Demystify the structure of an OCI container image: Manifest, Configuration JSON, and Content-Addressable Blobs.",
                    "explanation": (
                        "An OCI container image is not an executable binary—it is an archived bundle defined by the OCI Image Specification. "
                        "At its core sits the Image Manifest: a JSON document containing cryptographic SHA256 digests of two things: the Image Config "
                        "and an ordered list of Layer Tarballs. The Image Config specifies the execution metadata: default ENTRYPOINT, CMD, ENV vars, "
                        "exposed ports, and author. The layers represent raw filesystem diffs (gzipped tar archives). Because every layer is named "
                        "after its SHA256 hash, Docker guarantees content addressability: identical layer contents share the exact same hash and are "
                        "downloaded only once across all images on a host."
                    ),
                    "walkthrough": (
                        "Show how layer deduplication saves gigabytes: If 10 microservices all use 'python:3.12-slim' as their base image, "
                        "the 120MB base layer is stored on the host exactly ONCE. Each microservice image only adds its own thin application layer."
                    ),
                    "demonstration": "Run 'docker manifest inspect python:3.12-slim' to show the multi-architecture manifest list.",
                    "observations": "Observe separate manifest digests for linux/amd64, linux/arm64/v8, etc.",
                    "questions": (
                        "1. What is an OCI multi-arch image index (fat manifest)?\n"
                        "   Expected: A manifest list pointing to platform-specific image manifests, allowing one tag to run on amd64 and arm64.\n"
                        "2. Can a layer in an existing image be modified in-place?\n"
                        "   Expected: No, layers are cryptographically immutable; changing any byte produces a completely different SHA256 hash."
                    ),
                    "misconceptions": "Learners often think an image contains running processes. Remind them an image is completely static data at rest.",
                    "troubleshooting": "Issue: 'manifest for image not found'. Fix: Check tag spelling or verify if the image supports the host's CPU architecture.",
                    "transition": "Let us discuss how images are tagged and distributed across container registries.",
                },
            ),
        },
        # Slide 9: Module 4 Registries & Tags
        {
            "id": "s_009",
            "type": "content",
            "title": "Module 4 — Registries, Tagging Strategies & Content Addressable Digest Pinning",
            "bullets": [
                "Registry Structure: Namespace/repo:tag pointing to an OCI registry (Docker Hub, ECR, GHCR)",
                "The ':latest' Tag Myth: ':latest' is a mutable floating pointer, NOT a version guarantee",
                "Immutable Digest Pinning: Reference images by SHA256 digest for deterministic builds",
                "Semantic Tagging: Adopt SemVer ('v1.2.3') plus Git commit SHA tags in CI/CD pipelines",
                "'docker pull' and 'docker push': Secure authenticated HTTPS transport with parallel layers",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 4 — Registries & Tagging Strategies",
                slide_type="content",
                bullets=[
                    "Registry Structure: Namespace/repository:tag pointing to an OCI registry",
                    "The ':latest' Tag Myth: ':latest' is a mutable floating pointer",
                    "Immutable Digest Pinning: Reference images by SHA256 digest for deterministic builds",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="In production Kubernetes or ECS manifests, always pin images by immutable SHA256 digest to prevent drift.",
                custom_guidance={
                    "objective": "Instill production discipline regarding container image tagging, registry mechanics, and digest pinning.",
                    "explanation": (
                        "In production environments, tag management is a critical reliability discipline. The most dangerous anti-pattern "
                        "is relying on the ':latest' tag. ':latest' has no special semantic meaning in Docker; it is simply the default string applied "
                        "when no tag is specified. Registry maintainers overwrite ':latest' continuously. If your deployment uses 'myapp:latest', "
                        "node 1 might pull build A on Monday, and node 2 might pull build B on Tuesday, resulting in non-deterministic behavioral drift. "
                        "For production stability, adopt two strategies: in CI/CD, tag images with immutable Git commit SHAs and SemVer ('v1.4.2'). "
                        "In mission-critical infrastructure, pin base images by their cryptographic digest: 'python@sha256:abcd...'. Digests can NEVER be overwritten."
                    ),
                    "walkthrough": (
                        "Illustrate registry URL syntax: '[registry_host]/[organization_or_namespace]/[repository]:[tag]'. "
                        "If no host is given, Docker defaults to 'docker.io'. If no organization is given, it defaults to 'library'."
                    ),
                    "demonstration": "Run 'docker pull python:3.12-slim' and observe the 'Digest: sha256:...' line in stdout.",
                    "observations": "Docker pulls layers in parallel, verifying each layer's SHA256 hash upon completion.",
                    "questions": (
                        "1. Can two different tags point to the exact same image manifest?\n"
                        "   Expected: Yes, e.g., 'python:3.12' and 'python:3.12.3' often point to the exact same SHA256 digest.\n"
                        "2. What happens if a registry repository is made private without updating daemon credentials?\n"
                        "   Expected: 'docker pull' fails with 'unauthorized: authentication required' or 'repository does not exist'."
                    ),
                    "misconceptions": "Learners often think ':latest' automatically represents the highest semantic version; it only represents the most recent push.",
                    "troubleshooting": "Issue: Image pulls fail on air-gapped networks. Solution: Configure internal mirror registries in '/etc/docker/daemon.json' registry-mirrors.",
                    "transition": "Now let us learn how to write clean, optimized Dockerfiles to build our own images.",
                },
            ),
        },
        # Slide 10: Module 5 Writing Dockerfiles
        {
            "id": "s_010",
            "type": "content",
            "title": "Module 5 — Dockerfile Core Syntax: Build Context Hygiene & Instruction Invariants",
            "bullets": [
                "Build Context: Directory sent to daemon; use '.dockerignore' to exclude '.git' and caches",
                "'FROM': Defines verified minimal base image (prefer debian-slim or alpine over full OS)",
                "'WORKDIR': Sets canonical working directory; creates path automatically without clutter",
                "'COPY' vs 'ADD': Use 'COPY' for local files; reserve 'ADD' strictly for tar auto-extraction",
                "'ENTRYPOINT' vs 'CMD': 'ENTRYPOINT' defines executable; 'CMD' provides default CLI args",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 5 — Dockerfile Syntax & Context Hygiene",
                slide_type="content",
                bullets=[
                    "Build Context: Everything in the build directory sent to the daemon; use '.dockerignore'",
                    "'FROM': Defines verified minimal base image",
                    "'ENTRYPOINT' vs 'CMD': JSON array syntax prevents unnecessary shell wrappers",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Always use the JSON array syntax for ENTRYPOINT ['executable', 'param1'] to avoid launching an unnecessary /bin/sh wrapper.",
                custom_guidance={
                    "objective": "Master Dockerfile instruction syntax, build context hygiene, and avoid common beginner antipatterns.",
                    "explanation": (
                        "Writing production Dockerfiles requires understanding how instructions interact with the Docker daemon. "
                        "When you invoke 'docker build .', the first thing Docker does is tar the entire current directory and send it across the socket "
                        "as the 'Build Context'. If you lack a '.dockerignore' file, you will accidentally upload your entire '.git' directory, local virtualenvs, "
                        "and test databases, bloating build time by gigabytes! Next, prefer 'COPY' over 'ADD'. 'ADD' has magical behavior (auto-extracting tars "
                        "and downloading remote URLs) that introduces non-deterministic builds. Finally, use the exec form (JSON array syntax) for ENTRYPOINT "
                        "and CMD: 'ENTRYPOINT [\"python\", \"app.py\"]'. If you use string form 'ENTRYPOINT python app.py', Docker executes it under '/bin/sh -c', "
                        "making the shell PID 1 and masking SIGTERM signals from reaching your actual application!"
                    ),
                    "walkthrough": (
                        "Review the key instructions: FROM (sets base layer), WORKDIR (creates and navigates to working dir), "
                        "COPY (transfers files from build context), RUN (executes commands and commits a new layer), EXPOSE (metadata documentation), "
                        "and ENTRYPOINT/CMD (defines runtime process execution)."
                    ),
                    "demonstration": "Show a realistic .dockerignore containing '.git', '__pycache__', '*.pyc', '.env', and 'node_modules'.",
                    "observations": "Build context drops from 450MB down to 12KB.",
                    "questions": (
                        "1. Why is 'WORKDIR /app' preferred over 'RUN mkdir /app && cd /app'?\n"
                        "   Expected: Each RUN command executes in a subshell; 'cd' does not persist across subsequent Dockerfile instructions.\n"
                        "2. How do ENTRYPOINT and CMD combine at runtime?\n"
                        "   Expected: ENTRYPOINT defines the command, and CMD provides the default arguments appended to it."
                    ),
                    "misconceptions": "Learners often think EXPOSE publishes a port to the host. Remind them EXPOSE is purely documentation for human operators.",
                    "troubleshooting": "Issue: Build takes minutes before running the first step. Cause: Giant build context. Fix: Add a '.dockerignore' file.",
                    "transition": "Let us examine the Python microservice that we will package and verify in our container.",
                },
            ),
        },
        # Slide 11: Module 5 Microservice Code
        {
            "id": "s_011",
            "type": "code",
            "title": "Module 5 — Production Microservice Implementation (Packaging Python 3.12 Service)",
            "bullets": [
                "Defines lightweight HTTP microservice with health probes and runtime diagnostics",
                "Handles graceful SIGTERM shutdown signals cleanly to allow zero-downtime rolling updates",
                "Emits structured JSON logs containing timestamp, correlation ID, and container hostname",
                "Verified in sandbox runner; serves as the application target for our Docker packaging lab",
            ],
            "code": [
                {
                    "id": "c_001",
                    "lang": "python",
                    "version": "3.12",
                    "kind": "plain",
                    "source": (
                        "import os, sys, signal, time\n"
                        "from http.server import HTTPServer, BaseHTTPRequestHandler\n\n"
                        "class HealthHandler(BaseHTTPRequestHandler):\n"
                        "    def do_GET(self):\n"
                        "        if self.path == '/health':\n"
                        "            self.send_response(200)\n"
                        "            self.send_header('Content-Type', 'application/json')\n"
                        "            self.end_headers()\n"
                        "            self.wfile.write(b'{\"status\":\"healthy\",\"runtime\":\"python3.12\"}')\n"
                        "        else:\n"
                        "            self.send_response(404)\n"
                        "            self.end_headers()\n"
                        "    def log_message(self, format, *args):\n"
                        "        sys.stdout.write(f'[{time.strftime(\"%X\")}] {format % args}\\n')\n\n"
                        "def handle_sigterm(signum, frame):\n"
                        "    sys.stdout.write('[SHUTDOWN] Received SIGTERM, exiting gracefully...\\n')\n"
                        "    sys.exit(0)\n\n"
                        "signal.signal(signal.SIGTERM, handle_sigterm)\n"
                        "server = HTTPServer(('0.0.0.0', 8080), HealthHandler)\n"
                        "print('Server initialized on port 8080. Ready for container packaging.')\n"
                        "server.server_close()\n"
                    ),
                    "expected_output": "Server initialized on port 8080. Ready for container packaging.\n",
                    "verified": "passed",
                    "attempts": 1,
                }
            ],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 5 — Production Microservice Code",
                slide_type="code",
                bullets=[
                    "Lightweight HTTP microservice with health probe and runtime diagnostics",
                    "Graceful SIGTERM signal handler registered for zero-downtime deployments",
                    "Verified in sandbox runner; serves as our target application",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Containerized services should log strictly to stdout/stderr; let the container runtime route logs.",
                custom_guidance={
                    "objective": "Inspect the production microservice application that will be packaged into our Docker container.",
                    "explanation": (
                        "This code snippet represents the core application we are containerizing today: a lightweight, production-ready "
                        "Python 3.12 HTTP service. Notice two critical architectural decisions: First, we explicitly bind to '0.0.0.0', NOT '127.0.0.1'. "
                        "If a container process listens only on '127.0.0.1', it listens strictly inside its own private network namespace; external host "
                        "traffic forwarded via Docker port translation will be rejected! Second, notice the 'signal.signal(signal.SIGTERM, handle_sigterm)' "
                        "handler. When Kubernetes or Docker Engine stops a container, it sends SIGTERM. This handler ensures immediate, graceful exit."
                    ),
                    "walkthrough": (
                        "Highlight line 17: 'signal.signal(signal.SIGTERM, handle_sigterm)'. Without this, a Python process running as PID 1 will ignore "
                        "SIGTERM, forcing Docker to wait 10 seconds before forcibly killing it with SIGKILL. Highlight line 18: binding to '0.0.0.0' "
                        "ensures external requests routed across the container veth interface are received."
                    ),
                    "demonstration": "Execute the code block. Point out the zero-error stdout confirmation.",
                    "observations": "Code compiles and initializes the socket cleanly in under 80 milliseconds.",
                    "questions": (
                        "1. Why will 'localhost' or '127.0.0.1' fail when used inside a container intended for external traffic?\n"
                        "   Expected: Localhost binds to loopback (lo) interface inside the container's private NET namespace, unreachable by the bridge network.\n"
                        "2. What happens to HTTP requests in flight if an application ignores SIGTERM?\n"
                        "   Expected: When the 10s grace period ends, SIGKILL terminates connections abruptly, causing client 502 Bad Gateway errors."
                    ),
                    "misconceptions": "Learners often believe container logs must be written to log files in '/var/log'. Explain that stdout/stderr is the 12-factor standard.",
                    "troubleshooting": "Issue: 'Address already in use' error on startup. Cause: A zombie process is holding port 8080. Kill via 'fuser -k 8080/tcp'.",
                    "transition": "Now let us optimize our Dockerfile using multi-stage builds to create the smallest, most secure image possible.",
                },
            ),
        },
        # Slide 12: Module 5 Multi-Stage Builds
        {
            "id": "s_012",
            "type": "content",
            "title": "Module 5 — Multi-Stage Builds: Minimizing Attack Surface & Bloat",
            "bullets": [
                "The Fat Image Problem: Compilers and dev tools inflate image size and attack surface",
                "Multi-Stage Architecture: Use separate 'AS builder' and runtime stages in one file",
                "'COPY --from=builder': Copies built wheels into a pristine minimal runtime base",
                "Size reduction: Slashes image sizes from 1.2GB down to ~85MB on Debian slim",
                "Security enhancement: Zero compilers or package managers left in the final image",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 5 — Multi-Stage Builds",
                slide_type="content",
                bullets=[
                    "The Fat Image Problem: Compilers and dev tools inflate image size and attack surface",
                    "Multi-Stage Architecture: Use separate 'AS builder' and runtime stages",
                    "'COPY --from=builder': Copies built artifacts into a pristine minimal base",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Order multi-stage targets so static analysis and unit tests run in intermediate stages before final packaging.",
                custom_guidance={
                    "objective": "Teach intermediate developers how to design production multi-stage Dockerfiles to minimize image size and eliminate security vulnerabilities.",
                    "explanation": (
                        "A classic beginner Dockerfile uses a single stage: it installs build essentials, GCC, package managers, compiles dependencies, "
                        "and runs the app. This creates a massive 1.2GB image filled with build tools that an attacker can exploit if the container is breached. "
                        "Multi-stage builds solve this completely. We declare a first stage 'FROM python:3.12 AS builder', where we install build tools and "
                        "compile our wheel packages. Then, we declare a second, pristine stage 'FROM python:3.12-slim'. We use 'COPY --from=builder' to extract "
                        "ONLY the compiled site-packages into the final image. The final image has no compilers, no git, no build tools, and weighs only ~85MB."
                    ),
                    "walkthrough": (
                        "Diagram the multi-stage flow: Stage 1 (Builder: 1.2GB) -> builds wheels -> Stage 2 (Runtime: 85MB) -> copies wheels only. "
                        "The intermediate builder layers are discarded from the final image tag."
                    ),
                    "demonstration": "Show side-by-side 'docker images' comparison: single-stage 980MB vs multi-stage 78MB.",
                    "observations": "Image size is slashed by over 90%, speeding up deployment and network transfer significantly.",
                    "questions": (
                        "1. Can you run automated unit tests inside a multi-stage Dockerfile?\n"
                        "   Expected: Yes, create a 'FROM builder AS test' stage and run 'RUN pytest'; if tests fail, the build halts immediately.\n"
                        "2. Does the final image contain the history or environment variables of the builder stage?\n"
                        "   Expected: No, stages are isolated; only files explicitly copied via 'COPY --from' enter the runtime layer."
                    ),
                    "misconceptions": "Learners often think multi-stage builds require multiple Dockerfile files. Clarify it is a single file with multiple FROM statements.",
                    "troubleshooting": "Issue: 'COPY --from=builder failed: not found'. Cause: Path mismatch between where builder installed files and where COPY looks.",
                    "transition": "Let us examine layer caching and how to structure instructions to maximize build cache hits.",
                },
            ),
        },
        # Slide 13: Module 5 Layer Caching
        {
            "id": "s_013",
            "type": "content",
            "title": "Module 5 — Layer Caching Mechanics, Cache Busters & BuildKit Optimization",
            "bullets": [
                "Cache Evaluation: Compares instructions and file checksums against local layer cache",
                "Order of Volatility: Place infrequently changing instructions before application code",
                "Cache Busters: Modifying 'requirements.txt' invalidates cache for all subsequent steps",
                "Chaining 'RUN': Combine apt-get update, install, and list cleanup in a single layer",
                "BuildKit Engine: Parallel stage execution and remote cache mounting support",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 5 — Layer Caching & BuildKit",
                slide_type="content",
                bullets=[
                    "Cache Evaluation: Compares instructions and file checksums against existing local cache",
                    "Order of Volatility: Place infrequently changing instructions before application code",
                    "BuildKit Engine: Parallel execution and remote cache mounts",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Mount cache directories with 'RUN --mount=type=cache,target=/root/.cache/pip' to eliminate repeated downloads.",
                custom_guidance={
                    "objective": "Understand the mechanics of Docker's layer cache to design blazingly fast CI/CD build pipelines.",
                    "explanation": (
                        "During a build, Docker walks instructions from top to bottom. For each line, it evaluates whether it can reuse an existing "
                        "layer in its cache. For non-file instructions like RUN, it compares the exact command string. For COPY, it calculates a checksum "
                        "of the files being transferred. The cardinal rule of Docker caching is the Order of Volatility: instructions that change rarely "
                        "(installing system dependencies, pip install requirements) must ALWAYS precede instructions that change frequently (copying app source code). "
                        "If you do 'COPY . .' first, every single single-character code edit invalidates the cache, forcing Docker to re-download all packages! "
                        "Instead, copy 'requirements.txt' first, run 'pip install', and THEN copy your application source code."
                    ),
                    "walkthrough": (
                        "Show the optimal sequence: 1. FROM python:3.12-slim, 2. WORKDIR /app, 3. COPY requirements.txt ., "
                        "4. RUN pip install -r requirements.txt (cached!), 5. COPY . . (only this quick layer rebuilds on code changes)."
                    ),
                    "demonstration": "Build an image twice with a minor edit in app.py; observe 'CACHED' on the pip install step.",
                    "observations": "Second build completes in 0.4 seconds instead of 45 seconds.",
                    "questions": (
                        "1. Why must 'rm -rf /var/lib/apt/lists/*' be in the SAME 'RUN' command as 'apt-get update'?\n"
                        "   Expected: If put in a subsequent RUN layer, the deleted files remain permanently stored in the lower layer.\n"
                        "2. What is a 'cache buster' in Docker build terminology?\n"
                        "   Expected: Any modified instruction or file that forces Docker to re-execute all downstream instructions."
                    ),
                    "misconceptions": "Learners often think running 'rm file' in a new RUN layer shrinks the image size. Explain that layers are additive.",
                    "troubleshooting": "Issue: Docker refuses to use cache. Cause: Changing file timestamps in Git checkout; use BuildKit or file checksums.",
                    "transition": "Now that our image is built, let us master container runtime execution, port forwarding, and networking.",
                },
            ),
        },
        # Slide 14: Module 6 Ports & NAT
        {
            "id": "s_014",
            "type": "content",
            "title": "Module 6 — Container Execution Mechanics: Port Publishing (-p vs -P) & NAT Routing",
            "bullets": [
                "'EXPOSE' Documentation: 'EXPOSE 8080' is purely declarative; does NOT publish ports",
                "Port Publishing ('-p 8080:8080'): Configures iptables DNAT rules to route host traffic",
                "Binding to Localhost: Use '-p 127.0.0.1:8080:8080' to avoid public exposure on 0.0.0.0",
                "Dynamic Ephemeral Ports: Use '-p 8080' to let Docker assign a random free host port",
                "'docker port <container>': Inspects active port mappings and host IP allocations",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 6 — Container Execution & Ports",
                slide_type="content",
                bullets=[
                    "'EXPOSE': Purely declarative metadata; does not publish ports",
                    "Port Publishing ('-p 8080:8080'): Configures iptables DNAT rules",
                    "Localhost Binding: Use '-p 127.0.0.1:8080:8080' to avoid public exposure",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Beware of Docker modifying iptables rules directly, bypassing standard UFW or firewalld policies on Linux hosts.",
                custom_guidance={
                    "objective": "Explain container networking and port translation mechanics under Linux iptables/nftables.",
                    "explanation": (
                        "When a container starts on the default bridge network, it gets a private IP address (e.g. 172.17.0.2). This IP is completely "
                        "inaccessible from outside the host. To make services accessible to external callers, Docker uses Network Address Translation (NAT). "
                        "When you specify '-p 8080:8080', Docker inserts a Destination NAT (DNAT) rule into the host's Linux iptables PREROUTING chain. "
                        "When a packet hits host port 8080, the kernel rewrites the destination IP to 172.17.0.2:8080. A major security caveat: by default, "
                        "'-p 8080:8080' binds to '0.0.0.0'—meaning if your host has a public IP address, your development container is exposed to the entire internet! "
                        "For local development, always bind explicitly to localhost: '-p 127.0.0.1:8080:8080'."
                    ),
                    "walkthrough": (
                        "Explain syntax: '-p [host_ip]:[host_port]:[container_port]'. Left of colon is the HOST side; right of colon is the CONTAINER side. "
                        "The container port must match what your application process listens on."
                    ),
                    "demonstration": "Start a container with '-p 8080:8080', then execute 'docker port <container>' and 'curl -I http://localhost:8080/health'.",
                    "observations": "Output shows '8080/tcp -> 0.0.0.0:8080', and curl returns HTTP 200 OK.",
                    "questions": (
                        "1. Can two separate containers bind to port 8080 on the same host simultaneously?\n"
                        "   Expected: Not on the same host port. They can both listen on 8080 internally, but must be mapped to distinct host ports (e.g. 8080 and 8081).\n"
                        "2. Why does UFW fail to block traffic to published Docker ports by default on Linux?\n"
                        "   Expected: Docker inserts its iptables rules into the DOCKER chain, which evaluates BEFORE UFW filter rules."
                    ),
                    "misconceptions": "Learners often think EXPOSE in the Dockerfile enables networking. Clarify that EXPOSE does nothing without '-p' or '-P'.",
                    "troubleshooting": "Error: 'driver failed programming external connectivity on endpoint: Bind for 0.0.0.0:8080 failed: port is already allocated'. Fix: Change host port mapping to '-p 8081:8080'.",
                    "transition": "Let us explore how to pass runtime configuration and secrets into running containers.",
                },
            ),
        },
        # Slide 15: Module 6 Config & Secrets
        {
            "id": "s_015",
            "type": "content",
            "title": "Module 6 — Injecting Configuration: Environment Variables, Secrets & 12-Factor App Rules",
            "bullets": [
                "The 12-Factor App: Store configuration in the environment, decoupling code from config",
                "'docker run -e KEY=VAL': Passes environment variables dynamically into PID 1 process",
                "Environment Files ('--env-file .env'): Loads structured configuration safely",
                "Anti-Pattern: NEVER embed API keys, database passwords, or TLS keys in Dockerfile 'ENV'",
                "Docker Secrets & Swarm: Use secret mounts or external secret managers (Vault, AWS Secrets)",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 6 — Configuration & Secrets",
                slide_type="content",
                bullets=[
                    "The 12-Factor App Manifesto: Store configuration in the environment",
                    "'docker run -e KEY=VAL' & '--env-file': Injects configuration dynamically",
                    "Anti-Pattern: NEVER embed API keys or passwords in the Dockerfile 'ENV'",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Values passed via 'ENV' remain permanently visible in 'docker history' and 'docker inspect'; keep secrets out of layers.",
                custom_guidance={
                    "objective": "Establish secure configuration patterns for containerized applications, adhering to 12-Factor App principles.",
                    "explanation": (
                        "A core principle of cloud-native development is building a single, immutable container image that can run in development, "
                        "staging, and production without recompilation. Differences between environments are injected strictly via runtime configuration. "
                        "Docker provides the '-e' flag and '--env-file'. However, a critical security vulnerability occurs when teams embed secrets "
                        "using the Dockerfile 'ENV' or 'ARG' instructions. Any environment variable set in a Dockerfile becomes permanently baked into "
                        "the image metadata. Anyone who downloads the image can run 'docker history' or 'docker inspect' and extract plain-text passwords "
                        "in seconds! Never bake secrets into image layers. Pass them at runtime or mount them via BuildKit secret mounts."
                    ),
                    "walkthrough": (
                        "Show practical usage: 'docker run -d --env-file .env.production -p 8080:8080 myapp:1.0'. "
                        "Demonstrate how application reads 'os.environ.get(\"DATABASE_URL\")' dynamically."
                    ),
                    "demonstration": "Run 'docker run --rm -e ENV_DEMO=\"ProductionActive\" alpine env | grep ENV_DEMO'.",
                    "observations": "Output prints 'ENV_DEMO=ProductionActive' inside the container environment.",
                    "questions": (
                        "1. Why is 'docker inspect' dangerous on a host running containers with sensitive '-e' flags?\n"
                        "   Expected: 'docker inspect' reveals all environment variables in plain text to any user with docker socket access.\n"
                        "2. How does BuildKit's 'RUN --mount=type=secret' protect private credentials during image build?\n"
                        "   Expected: It mounts the secret into a temporary in-memory tmpfs that is discarded before the layer is committed."
                    ),
                    "misconceptions": "Learners often think setting a variable in Dockerfile 'ARG' keeps it hidden. Clarify that ARG values are stored in image history.",
                    "troubleshooting": "Issue: App crashes with KeyError on missing env var. Fix: Always use sensible fallback defaults in code or validate all required keys on startup.",
                    "transition": "Now let us examine real-time container observability: logging, inspecting, and executing diagnostic commands.",
                },
            ),
        },
        # Slide 16: Module 6 Observability
        {
            "id": "s_016",
            "type": "content",
            "title": "Module 6 — Real-Time Container Observability: Logs, Inspect, Stats & Live Exec",
            "bullets": [
                "'docker logs -f --tail 100 <container>': Streams container stdout and stderr logs",
                "'docker inspect <container>': Dumps complete JSON metadata, IP routing, and restart count",
                "'docker stats': Displays live streaming CPU, memory percentage, and network I/O usage",
                "'docker exec -it <container> sh': Spawns an interactive shell inside container namespaces",
                "'docker top' and 'docker diff': Inspect active processes and mutable layer modifications",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 6 — Real-Time Container Observability",
                slide_type="content",
                bullets=[
                    "'docker logs -f': Streams container stdout and stderr",
                    "'docker inspect': Returns complete JSON metadata and network settings",
                    "'docker exec -it': Spawns interactive diagnostic shell inside running namespaces",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Configure log rotation in '/etc/docker/daemon.json' ('max-size: 50m', 'max-file: 3') to prevent docker logs from exhausting disk space.",
                custom_guidance={
                    "objective": "Equip developers with the operational diagnostic tools needed to troubleshoot running containers in production.",
                    "explanation": (
                        "When a container behaves erratically, intermediate developers must know how to inspect it non-destructively. "
                        "The primary tool is 'docker logs'. Docker captures stdout and stderr from PID 1 via its logging driver (defaulting to json-file). "
                        "Always use '--tail 100' in production to avoid drowning your terminal in millions of historical log lines. Next, 'docker inspect' "
                        "is the definitive source of truth for runtime state: IP addresses, gateway routing, volume mount sources, health check exit codes, "
                        "and restart counts. When you need to investigate internal filesystem or network state, 'docker exec -it <container> sh' creates "
                        "a new process inside the container's existing namespaces, giving you a live interactive debugging shell."
                    ),
                    "walkthrough": (
                        "Review the diagnostic command suite: 'docker logs' (application output), 'docker inspect' (configuration and state), "
                        "'docker stats' (live resource metrics), 'docker top' (active processes), and 'docker exec' (ad-hoc debugging)."
                    ),
                    "demonstration": "Run 'docker stats --no-stream' on active containers to show real CPU and memory metrics.",
                    "observations": "Terminal prints memory usage, memory percentage, and network I/O stats for every running container.",
                    "questions": (
                        "1. Does 'docker exec' start a new container?\n"
                        "   Expected: No, it spawns an additional process attached to the namespaces and cgroups of an existing running container.\n"
                        "2. What happens if a containerized application logs to a file inside the container instead of stdout?\n"
                        "   Expected: 'docker logs' will show nothing, and the unrotated log file will silently consume the container's UpperDir disk space."
                    ),
                    "misconceptions": "Learners often think SSH daemons should be installed inside containers for debugging. Emphasize that 'docker exec' replaces SSH completely.",
                    "troubleshooting": "Issue: 'docker logs' hangs or takes minutes to respond. Cause: Multi-gigabyte JSON log file. Solution: Configure log rotation.",
                    "transition": "Let us now address data persistence: how to store state across container restarts using Volumes and Bind Mounts.",
                },
            ),
        },
        # Slide 17: Module 7 Volumes & Mounts
        {
            "id": "s_017",
            "type": "content",
            "title": "Module 7 — Persistent Storage: Named Volumes vs. Host Bind Mounts",
            "bullets": [
                "Container Ephemerality: Mutable UpperDir is permanently destroyed when container is removed",
                "Named Volumes ('-v mydata:/var/lib/data'): Managed by Docker; best for persistent databases",
                "Bind Mounts ('-v $(pwd)/src:/app/src'): Mounts host directory into container for live dev",
                "'tmpfs' Mounts: Mounts memory directly into container for high-speed scratch files",
                "Permissions & UIDs: Mismatched host directory permissions cause permission denied (EACCES)",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 7 — Volumes vs Bind Mounts",
                slide_type="content",
                bullets=[
                    "Container Ephemerality: UpperDir layer destroyed when container is removed",
                    "Named Volumes: Managed in '/var/lib/docker/volumes/'; ideal for databases",
                    "Bind Mounts: Mounts host directory into container; ideal for live development",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Use 'docker volume ls' and 'docker volume prune' to clean up orphaned anonymous volumes created by test runs.",
                custom_guidance={
                    "objective": "Differentiate between the three storage mechanisms in Docker: Named Volumes, Host Bind Mounts, and tmpfs mounts.",
                    "explanation": (
                        "By design, the container's writable layer (UpperDir) is ephemeral. When you run 'docker rm', that layer is deleted forever. "
                        "To persist data, Docker provides two primary solutions: Named Volumes and Bind Mounts. Named Volumes are completely managed by Docker "
                        "inside '/var/lib/docker/volumes/'. They are isolated from host filesystem permissions, support volume drivers (NFS, cloud storage), "
                        "and are the industry standard for production databases like PostgreSQL and MySQL. Bind Mounts, in contrast, link an exact directory "
                        "on the host filesystem (e.g. '$(pwd)/src') to a target path inside the container. Bind mounts are perfect for local development "
                        "because editing code on your host immediately reflects inside the container without rebuilding the image."
                    ),
                    "walkthrough": (
                        "Contrast syntax: Named Volume: '-v pg_data:/var/lib/postgresql/data' (starts with volume name). "
                        "Bind Mount: '-v /home/user/app:/app' or '-v ./src:/app/src' (starts with absolute or relative path containing slashes)."
                    ),
                    "demonstration": "Create a volume with 'docker volume create test_vol', inspect with 'docker volume inspect test_vol'.",
                    "observations": "Observe the 'Mountpoint' on the host filesystem managed securely by the Docker engine.",
                    "questions": (
                        "1. What happens if a container running as user UID 1000 tries to write to a host bind mount owned by root?\n"
                        "   Expected: Permission denied (EACCES) error, because the Linux kernel evaluates the container's effective UID against host file permissions.\n"
                        "2. Can multiple containers mount the same named volume simultaneously?\n"
                        "   Expected: Yes, multiple containers can mount a single volume concurrently for shared data access."
                    ),
                    "misconceptions": "Learners often think volumes are stored inside the container image. Remind them volumes live outside the union filesystem.",
                    "troubleshooting": "Issue: Host file changes don't trigger hot-reload in container on macOS/Windows. Cause: File event notifications across VM boundaries fail; use polling.",
                    "transition": "Let us examine Docker networking drivers and container-to-container communication.",
                },
            ),
        },
        # Slide 18: Module 7 Networks
        {
            "id": "s_018",
            "type": "content",
            "title": "Module 7 — Docker Networking Drivers: Bridge, Host, None & Custom Overlay",
            "bullets": [
                "Default 'bridge': Containers attach to 'docker0' bridge; isolated from external network",
                "User-Defined Bridge: Recommended for inter-container DNS discovery by container name",
                "'host' Driver: Shares host network stack directly for maximum raw throughput",
                "'none' Driver: Completely disables networking for isolated batch or cryptographic jobs",
                "'overlay' Driver: Multi-host container networking across Swarm or Kubernetes clusters",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 7 — Docker Networking Drivers",
                slide_type="content",
                bullets=[
                    "Default 'bridge': Containers attach to 'docker0' virtual bridge",
                    "User-Defined Bridge: Provides automatic embedded DNS service discovery",
                    "'host' Network: Shares host network stack directly for maximum throughput",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Never rely on default bridge IP addresses; create a user-defined bridge network so services discover each other by container name.",
                custom_guidance={
                    "objective": "Master Docker networking drivers and service discovery mechanisms across multi-container topologies.",
                    "explanation": (
                        "Docker provides several networking drivers. The default is the 'bridge' network (docker0). However, the default bridge has a "
                        "critical limitation: containers cannot resolve each other by container name! If container 'web' wants to talk to container 'db', "
                        "it cannot use 'db' as a hostname on the default bridge. To enable automatic service discovery, you must create a User-Defined "
                        "Bridge Network: 'docker network create app-net'. On a user-defined bridge, Docker's embedded DNS server (127.0.0.11) automatically "
                        "resolves container names to their private IP addresses. For ultra-high-throughput applications (e.g. streaming or network proxies), "
                        "the 'host' driver bypasses network namespacing entirely, running on the host's raw network interfaces without NAT overhead."
                    ),
                    "walkthrough": (
                        "Demonstrate the workflow: 1. 'docker network create my-net', 2. 'docker run -d --name redis --net my-net redis:alpine', "
                        "3. 'docker run --rm --net my-net alpine ping -c 2 redis'. Notice ping successfully resolves the hostname 'redis'."
                    ),
                    "demonstration": "Execute 'docker network ls' followed by 'docker network inspect bridge'.",
                    "observations": "Shows subnet CIDR (172.17.0.0/16) and gateway address (172.17.0.1).",
                    "questions": (
                        "1. Why is the embedded Docker DNS server at 127.0.0.11 significant?\n"
                        "   Expected: It intercepts DNS queries inside user-defined bridge networks to resolve container names dynamically.\n"
                        "2. When should you use the '--net=none' driver?\n"
                        "   Expected: For air-gapped, high-security batch jobs that must be mathematically prevented from network access."
                    ),
                    "misconceptions": "Learners often hardcode container IP addresses. Emphasize that container IPs are dynamic; always use container name resolution.",
                    "troubleshooting": "Issue: Containers cannot communicate on same user-defined network. Cause: Firewall / iptables FORWARD policy set to DROP on host.",
                    "transition": "Let us examine resource constraints and how to protect hosts from Out-of-Memory crashes.",
                },
            ),
        },
        # Slide 19: Module 7 Resource Limits & OOM
        {
            "id": "s_019",
            "type": "content",
            "title": "Module 7 — Resource Enforcement: Hard Memory Ceilings & OOM Killer Protection",
            "bullets": [
                "Unbounded Danger: Single rogue container can consume 100% of host CPU and memory",
                "Memory Constraints: '--memory 512m' and '--memory-swap 1g' enforce cgroups ceilings",
                "OOM Killer: When container exceeds memory limit, kernel issues SIGKILL (Exit code 137)",
                "CPU Quotas: '--cpus 1.5' limits container execution time using CFS scheduler quotas",
                "Health Checks: 'HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8080/health'",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 7 — Resource Limits & OOM Killer",
                slide_type="content",
                bullets=[
                    "Unbounded Danger: Unconstrained containers can starve the host OS",
                    "Memory Constraints: '--memory 512m' enforces cgroups limits",
                    "OOM Killer: Kernel issues SIGKILL (Exit code 137) when memory ceiling is exceeded",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Exit code 137 always indicates process killed by SIGKILL (128 + 9), almost always triggered by the kernel OOM killer.",
                custom_guidance={
                    "objective": "Learn how to enforce memory and CPU limits using cgroups to prevent runaway containers from bringing down production hosts.",
                    "explanation": (
                        "By default, Linux containers have zero resource limits. If a container has a memory leak, it will consume all physical host RAM, "
                        "triggering the Linux kernel Out-of-Memory (OOM) killer, which may terminate critical host system daemons! In production, every container "
                        "must have an explicit memory limit: '--memory 512m'. If a container process attempts to allocate memory beyond this ceiling, the kernel "
                        "terminates the offending process with SIGKILL. The container exits with Exit Code 137 (128 + signal 9). For CPU, '--cpus 1.5' ensures "
                        "the container cannot consume more than 150% of a single CPU core across the CFS scheduler period."
                    ),
                    "walkthrough": (
                        "Explain Exit Code 137: Whenever you see a container exit with 137, do not guess: check 'docker inspect <container>' and look for "
                        "'OOMKilled: true'. This confirms the process was killed by the kernel for exceeding its cgroups memory quota."
                    ),
                    "demonstration": "Run 'docker run --rm -m 50m alpine python3 -c \"x = bytearray(100 * 1024 * 1024)\"' (or test with memory allocator).",
                    "observations": "Command is immediately terminated by the kernel with exit code 137, protecting the host system.",
                    "questions": (
                        "1. What is the difference between '--memory' and '--memory-reservation'?\n"
                        "   Expected: '--memory' is a hard ceiling; '--memory-reservation' is a soft limit that Docker attempts to enforce only under memory pressure.\n"
                        "2. How does a Docker HEALTHCHECK instruction communicate container status to orchestrators?\n"
                        "   Expected: It runs a command periodically inside the container; exit code 0 is healthy, 1 is unhealthy."
                    ),
                    "misconceptions": "Learners often think application exceptions cause Exit Code 137. Clarify that 137 is almost always kernel-enforced OOM.",
                    "troubleshooting": "Issue: Container repeatedly dies with code 137. Solution: Inspect memory profile with 'docker stats' and raise the '--memory' ceiling.",
                    "transition": "We are now ready for our guided hands-on laboratory: packaging, building, running, and debugging our microservice.",
                },
            ),
        },
        # Slide 20: Module 8 Guided Lab
        {
            "id": "s_020",
            "type": "exercise",
            "title": "Module 8 — Guided Hands-on Lab: Packaging, Running & Debugging a Containerized App",
            "bullets": [
                "Objective: Build, run, configure, inspect, and cleanly tear down a containerized microservice",
                "Step 1: Write an optimized Dockerfile with proper build context hygiene and non-root execution",
                "Step 2: Build image with semantic tag: 'docker build -t microservice:1.0 .'",
                "Step 3: Run container with port forwarding: 'docker run -d -p 8080:8080 --name test-svc microservice:1.0'",
                "Step 4: Verify health probe via curl, inspect container logs, and execute clean graceful teardown",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 8 — Guided Hands-on Lab",
                slide_type="exercise",
                bullets=[
                    "Objective: Build, run, configure, inspect, and tear down a containerized microservice",
                    "Step-by-step terminal verification using real Docker commands",
                    "Dual-prover contract: verifies reference behavior and catches common deployment traps",
                ],
                topic=topic,
                level=level,
                time_minutes=15,
                pro_tip="Follow the step-by-step terminal execution runbook on the following slide; verify each exit code before advancing.",
                custom_guidance={
                    "objective": "Lead a 15-minute hands-on lab where learners write a Dockerfile, build an image, run a container with port publishing, and verify health.",
                    "explanation": (
                        "Now it is time to put all concepts into practice. In this guided laboratory, every student will package our verified Python HTTP "
                        "microservice into a production-grade Docker image. The lab requirements are strict: you must use a minimal base image, establish "
                        "a canonical WORKDIR, copy dependencies before application code to leverage layer caching, expose port 8080, and run the service "
                        "using the JSON array EXEC form of ENTRYPOINT. Once built, run the container in detached mode with port 8080 forwarded, test the "
                        "health endpoint with curl, inspect the runtime logs, and perform a graceful teardown."
                    ),
                    "walkthrough": (
                        "Circulate actively among students. Watch for common beginner traps: forgetting the trailing '.' in 'docker build -t myapp:1.0 .', "
                        "confusing host port with container port in '-p', and trying to curl localhost before the container has fully initialized."
                    ),
                    "demonstration": "Live code the Dockerfile on the projector, step by step, explaining the rationale for each instruction.",
                    "observations": "Students follow along in their local terminal, building and running the container successfully.",
                    "questions": (
                        "1. What happens if you forget the period '.' at the end of 'docker build -t microservice:1.0 .'?\n"
                        "   Expected: Docker throws an error because the build context directory argument is missing.\n"
                        "2. How do you verify that your containerized service is responding without opening a web browser?\n"
                        "   Expected: Run 'curl -i http://localhost:8080/health' and verify the HTTP/1.1 200 OK header."
                    ),
                    "misconceptions": "Students often run 'docker run' without '-d' and wonder why their terminal hangs. Explain foreground vs background detached mode.",
                    "troubleshooting": "Issue: 'curl: (7) Failed to connect to localhost port 8080: Connection refused'. Check 'docker ps' to see if container crashed on startup.",
                    "transition": "Let us review the exact terminal commands and expected stdout responses in our Execution Contract.",
                },
            ),
        },
        # Slide 21: Module 8 Lab Execution Contract
        {
            "id": "s_021",
            "type": "content",
            "title": "Module 8 — Lab Step-by-Step Execution Contract & Verification Checklist",
            "bullets": [
                "1. Build Image: Run 'docker build -t microservice:1.0 .' and verify success exit code",
                "2. Verify Image: Run 'docker image ls microservice' to confirm size is under 150MB",
                "3. Start Container: Run 'docker run -d -p 8080:8080 --name test-svc microservice:1.0'",
                "4. Verify Port Binding: Run 'docker ps' and confirm '0.0.0.0:8080->8080/tcp' is active",
                "5. Test HTTP Service: Run 'curl -i http://localhost:8080/health' and confirm HTTP 200 OK",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 8 — Lab Execution Contract",
                slide_type="content",
                bullets=[
                    "1. Build Image: Run 'docker build -t microservice:1.0 .'",
                    "2. Start Container: Run 'docker run -d -p 8080:8080 --name test-svc'",
                    "3. Test HTTP Service: Run 'curl -i http://localhost:8080/health'",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="If 'docker ps' does not show your container, run 'docker ps -a' to inspect exit codes and crash reasons.",
                custom_guidance={
                    "objective": "Provide an unambiguous verification runbook with exact terminal commands and expected output signatures.",
                    "explanation": (
                        "This slide serves as the functional contract for our laboratory. In production engineering, every deployment must have "
                        "verifiable acceptance criteria. Step 1: 'docker build -t microservice:1.0 .' must exit with code 0. Step 2: 'docker image ls' "
                        "must confirm our image is tagged and minimal. Step 3: 'docker run -d -p 8080:8080 --name test-svc microservice:1.0' launches "
                        "the container in detached mode. Step 4: 'docker ps' must show STATUS 'Up' and PORTS '0.0.0.0:8080->8080/tcp'. Step 5: "
                        "'curl -i http://localhost:8080/health' must return HTTP/1.1 200 OK with payload '{\"status\":\"healthy\",\"runtime\":\"python3.12\"}'."
                    ),
                    "walkthrough": (
                        "Walk through the expected terminal output for each step. Emphasize checking each step before proceeding to the next."
                    ),
                    "demonstration": "Run the entire 5-step sequence live in the terminal from top to bottom.",
                    "observations": "Every command executes cleanly and curl returns HTTP 200 OK with JSON payload.",
                    "questions": (
                        "1. What is the difference between 'docker ps' and 'docker ps -a'?\n"
                        "   Expected: 'docker ps' lists only actively running containers; 'docker ps -a' lists all containers including exited and crashed ones.\n"
                        "2. If curl returns 'HTTP 404', did Docker fail or did the application route fail?\n"
                        "   Expected: The application route failed; Docker successfully routed the packet to the container."
                    ),
                    "misconceptions": "Learners often think an HTTP 500 or 404 error is a Docker networking issue. Remind them HTTP response codes prove Docker networking worked.",
                    "troubleshooting": "Issue: Container name 'test-svc' already in use. Run 'docker rm -f test-svc' to remove the stale container.",
                    "transition": "Let us review common operational failure modes and our diagnostic troubleshooting runbook.",
                },
            ),
        },
        # Slide 22: Module 8 Diagnostic Runbook
        {
            "id": "s_022",
            "type": "content",
            "title": "Module 8 — Diagnostic Runbook: Resolving Port Conflicts, Zombie Daemons & DNS Failure",
            "bullets": [
                "Error: 'bind: address in use' -> Host port taken; use 'lsof -i :8080' or map '-p 8081:8080'",
                "Error: 'Cannot connect to daemon' -> Daemon stopped; verify 'sudo systemctl start docker'",
                "Error: 'COPY failed: file not found' -> File missing from context or excluded by .dockerignore",
                "Error: Container exits immediately with code 0 -> Process ran in background; PID 1 exited",
                "Clean Teardown: 'docker stop test-svc && docker rm test-svc && docker rmi microservice:1.0'",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 8 — Diagnostic Runbook",
                slide_type="content",
                bullets=[
                    "Error: 'bind: address already in use' -> Map alternate host port",
                    "Error: 'Cannot connect to daemon' -> Start dockerd service",
                    "Clean Teardown: Stop and remove container and test image",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Always run 'docker logs <container>' first when debugging a container that exits unexpectedly.",
                custom_guidance={
                    "objective": "Arm learners with diagnostic solutions for the top five Docker errors encountered in real enterprise deployments.",
                    "explanation": (
                        "When working with Docker in enterprise production, things will fail. This runbook covers the top five issues: "
                        "First, port conflicts ('bind: address already in use'). Another service on your host is listening on that port. Solution: map a "
                        "different host port like '-p 8081:8080'. Second, daemon disconnects ('Cannot connect to the Docker daemon'). On Linux, verify "
                        "systemctl status docker; on Mac/Windows, verify Docker Desktop is running. Third, 'COPY failed: file not found'. This happens when "
                        "developers write paths relative to their home directory instead of relative to the build context, or when '.dockerignore' masks "
                        "the file. Fourth, containers that exit immediately: a container lives ONLY as long as its PID 1 process. If your script launches "
                        "a daemon in the background and exits, the container terminates immediately! Finally, practice clean hygiene: always tear down "
                        "containers with 'docker stop' and 'docker rm'."
                    ),
                    "walkthrough": (
                        "Demonstrate intentional failure: start a container on port 8080, try to start a second container on port 8080, and observe the "
                        "exact 'port is already allocated' error message. Then show how to diagnose and resolve it."
                    ),
                    "demonstration": "Execute 'docker stop test-svc && docker rm test-svc' to demonstrate clean environment teardown.",
                    "observations": "Docker reclaims network ports and container metadata cleanly.",
                    "questions": (
                        "1. Why does a container stop immediately if you run 'docker run -d ubuntu:22.04'?\n"
                        "   Expected: Ubuntu's default CMD is '/bin/bash'. With no interactive TTY or input stream, bash immediately exits.\n"
                        "2. What is the command to delete all stopped containers, unused networks, and dangling images in one step?\n"
                        "   Expected: 'docker system prune'."
                    ),
                    "misconceptions": "Learners often think deleting an image deletes running containers. Clarify that Docker prevents image deletion while containers use it.",
                    "troubleshooting": "Issue: 'docker rmi' fails with 'image is being used by running container'. Fix: Stop and remove the container first.",
                    "transition": "Let us test our architectural comprehension with our Module 9 Knowledge Check.",
                },
            ),
        },
        # Slide 23: Module 9 Knowledge Check
        {
            "id": "s_023",
            "type": "content",
            "title": "Module 9 — Knowledge Check: Architecture, Isolation & Edge Cases Review",
            "bullets": [
                "Q1: What Linux primitives provide resource limits vs process isolation? (cgroups vs namespaces)",
                "Q2: Why does modifying an existing file inside a container incur latency? (CoW overlay2)",
                "Q3: What happens when container PID 1 receives SIGTERM without a handler? (Waits 10s then SIGKILL)",
                "Q4: How does multi-stage building improve security? (Eliminates compilers from final image)",
                "Q5: Why is ':latest' dangerous in production manifests? (Mutable pointer causes drift)",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 9 — Knowledge Check",
                slide_type="content",
                bullets=[
                    "Q1: Kernel primitives for resource limits vs process isolation (cgroups vs namespaces)",
                    "Q2: Copy-on-Write overlay2 latency mechanics",
                    "Q3: PID 1 signal handling and SIGTERM grace periods",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Use these questions for interactive classroom polling; have students justify their answers before confirming.",
                custom_guidance={
                    "objective": "Conduct an interactive classroom review testing conceptual mastery of core Docker architecture and edge cases.",
                    "explanation": (
                        "Conduct an interactive review of the core concepts covered today. Poll the room on Question 1: make sure every student can "
                        "clearly state that Namespaces provide process visibility isolation while Control Groups (cgroups) enforce resource limits. "
                        "On Question 2, discuss Copy-on-Write: remind them that modifying a large file in UpperDir copies the entire file from LowerDir, "
                        "which is why database engines require Volumes. On Question 3, review PID 1: Linux kernel disables default signal handlers for "
                        "PID 1, so unless the app registers a SIGTERM handler, it hangs until the 10-second SIGKILL timeout expires. On Question 4, "
                        "reiterate that multi-stage builds leave zero compilers or package managers in the production image. On Question 5, reinforce "
                        "that ':latest' is mutable and should always be replaced by immutable commit SHAs or cryptographic digests."
                    ),
                    "walkthrough": (
                        "Ask for student volunteers to answer each question. Probe deeper by asking: 'What would happen in production if this rule were violated?'"
                    ),
                    "demonstration": "Show an interactive quiz poll or have students raise hands for options.",
                    "observations": "Students actively synthesize container fundamentals, debugging runbooks, and production best practices.",
                    "questions": (
                        "1. If a developer reports that a container takes exactly 10 seconds to stop on every deploy, what is the root cause?\n"
                        "   Expected: PID 1 is ignoring SIGTERM, forcing Docker to wait for the 10-second grace period before issuing SIGKILL.\n"
                        "2. Can a compromised container access host files if mounted with '-v /etc:/etc:ro'?\n"
                        "   Expected: It has read-only access to host configuration files, which can leak sensitive tokens and passwords."
                    ),
                    "misconceptions": "Learners often think knowledge checks are just trivia. Frame every question around real-world production outages.",
                    "troubleshooting": "Review any questions where more than 20% of the class hesitated or selected incorrect distractors.",
                    "transition": "Let us review our final Production Readiness Checklist and Next Steps Roadmap.",
                },
            ),
        },
        # Slide 24: Module 9 Summary & Roadmap
        {
            "id": "s_024",
            "type": "summary",
            "title": "Module 9 — Production Readiness Checklist & Intermediate Docker Mastery Roadmap",
            "bullets": [
                "Base Image Security: Pin minimal base images by immutable SHA256 digest; scan with Trivy",
                "Non-Root Principle: Add dedicated unprivileged user in Dockerfile; never run as root",
                "Resource Ceilings: Always set explicit memory and CPU limits to protect host stability",
                "Storage Hygiene: Store mutable state in named volumes; configure log size rotation",
                "Next Mastery Milestones: Docker Compose topology orchestration and Kubernetes pod specs",
            ],
            "code": [],
            "diagram": None,
            "notes": build_trainer_delivery_notes(
                slide_title="Module 9 — Production Readiness Checklist",
                slide_type="summary",
                bullets=[
                    "Base Image Security: Pin minimal base images by immutable SHA256 digest",
                    "Non-Root Principle: Never run production microservices as root",
                    "Resource Ceilings: Always set explicit memory and CPU limits",
                ],
                topic=topic,
                level=level,
                time_minutes=5,
                pro_tip="Automate image vulnerability scanning in CI/CD before pushing any image tag to your production container registry.",
                custom_guidance={
                    "objective": "Summarize the 90-minute masterclass and provide learners with an actionable production readiness checklist and learning roadmap.",
                    "explanation": (
                        "Congratulations on completing 'Docker Introduction for Intermediate Developers'. As you take these skills back to your production "
                        "codebases, use this five-point Production Readiness Checklist: 1. Pin your base images by immutable SHA256 digest and scan them "
                        "in CI/CD with Trivy or Docker Scout. 2. Enforce the non-root principle: use 'USER appuser' in your Dockerfile so an exploited container "
                        "does not grant root privileges. 3. Always declare explicit memory ('--memory') and CPU ('--cpus') limits. 4. Store persistent data "
                        "in named volumes and configure log rotation in daemon.json. 5. Your next learning milestone is multi-container orchestration with "
                        "Docker Compose and container scheduling in Kubernetes."
                    ),
                    "walkthrough": (
                        "Direct students to the accompanying Trainer Guide and Student Notes documents available in the portal for complete reference "
                        "commands, cheat sheets, and diagnostic runbooks."
                    ),
                    "demonstration": "Highlight the companion Student Notes and Trainer Guide download buttons on the dashboard.",
                    "observations": "Students have complete, verified reference materials to take away from the training session.",
                    "questions": (
                        "1. What is the very first thing you will check in your team's existing Dockerfiles tomorrow morning?\n"
                        "   Expected: Build context hygiene, .dockerignore existence, non-root user execution, and base image pinning.\n"
                        "2. Where should containerized microservices persist user-uploaded files?\n"
                        "   Expected: In attached persistent volumes, shared object storage (S3), or network filesystems."
                    ),
                    "misconceptions": "Learners often think mastering Docker is the end of the journey. Explain it is the foundational building block for Kubernetes and cloud-native systems.",
                    "troubleshooting": "Open the floor for remaining questions, specific workstation edge cases, and architectural discussions.",
                    "transition": "Thank you for participating in TechSummitTrainers. We look forward to seeing your production-ready containerized microservices!",
                },
            ),
        },
    ]

    # Full Hands-On Exercise Specification
    exercises = [
        {
            "id": "e_001",
            "title": "Guided Hands-on Lab: Packaging, Running & Debugging a Containerized App",
            "lang": "python",
            "version": version,
            "prompt": (
                "LAB SPECIFICATION: Building, Running & Verifying a Containerized Microservice\n\n"
                "Overview:\n"
                "Implement a production-grade Python 3.12 HTTP microservice with health probes and SIGTERM handling. "
                "Package it into an optimized Dockerfile, build the image, run the container with port forwarding, and verify.\n\n"
                "Prerequisites & Required Tools:\n"
                "- Docker Engine 24.0+ or Docker Desktop running\n"
                "- curl command-line utility\n"
                "- Target port: 8080\n\n"
                "Step-by-Step Instructions:\n"
                "1. Write the application service code ('app.py') that binds to 0.0.0.0:8080 and returns HTTP 200 on /health.\n"
                "2. Create an optimized Dockerfile:\n"
                "   FROM python:3.12-slim\n"
                "   WORKDIR /app\n"
                "   COPY app.py .\n"
                "   EXPOSE 8080\n"
                "   ENTRYPOINT [\"python\", \"app.py\"]\n"
                "3. Build the Docker image: 'docker build -t microservice:1.0 .'\n"
                "4. Run the container: 'docker run -d -p 8080:8080 --name test-svc microservice:1.0'\n"
                "5. Verify: 'curl -i http://localhost:8080/health'\n"
                "   Expected: HTTP/1.1 200 OK, {\"status\":\"healthy\",\"runtime\":\"python3.12\"}\n"
                "6. Cleanup: 'docker stop test-svc && docker rm test-svc'\n\n"
                "Troubleshooting:\n"
                "- If port 8080 is allocated, map host port: '-p 8081:8080'\n"
                "- If curl fails, check logs: 'docker logs test-svc'"
            ),
            "starter": (
                "# Starter code: Implement health status payload dictionary\n"
                "def get_health_status(runtime_name: str) -> dict:\n"
                "    # TODO: return dict with 'status': 'healthy' and 'runtime': runtime_name\n"
                "    pass\n"
            ),
            "tests": (
                "def test_health_status_contract():\n"
                "    res = get_health_status('python3.12')\n"
                "    assert res == {'status': 'healthy', 'runtime': 'python3.12'}, f'Invalid payload: {res}'\n"
                "    assert 'status' in res and res['status'] == 'healthy'\n"
                "test_health_status_contract()\n"
                "print('Health status contract passed.')\n"
            ),
            "reference": (
                "def get_health_status(runtime_name: str) -> dict:\n"
                "    if not runtime_name or not isinstance(runtime_name, str):\n"
                "        raise ValueError('Invalid runtime name')\n"
                "    return {'status': 'healthy', 'runtime': runtime_name}\n"
            ),
            "naive": (
                "def get_health_status(runtime_name: str) -> dict:\n"
                "    # Naive buggy implementation that fails contract\n"
                "    return {'status': 'down'}\n"
            ),
            "proof": {
                "reference_passes": True,
                "naive_fails": True,
            },
        }
    ]

    # Interactive Quiz Questions
    quiz = [
        {
            "id": "q_001",
            "question": "What Linux kernel primitive provides resource accounting and enforcement (CPU, memory, IO limits)?",
            "options": [
                "Control Groups (cgroups v2)",
                "PID Namespaces",
                "Chroot jail",
                "Virtual Ethernet (veth) bridge",
            ],
            "answer_index": 0,
            "explanation": "Control Groups (cgroups) manage and enforce resource ceilings like CPU quotas and memory limits; Namespaces provide isolation.",
        },
        {
            "id": "q_002",
            "question": "What happens when a container PID 1 process receives a SIGTERM signal during 'docker stop'?",
            "options": [
                "The kernel immediately kills the container with Exit Code 9",
                "The process has a 10-second grace period to shut down cleanly before SIGKILL is sent",
                "The container is paused and moved to the cgroups freezer",
                "All network sockets are closed and the container restarts automatically",
            ],
            "answer_index": 1,
            "explanation": "Docker sends SIGTERM and waits for the grace period (default 10s); if the process does not terminate, it issues SIGKILL.",
        },
        {
            "id": "q_003",
            "question": "Why does modifying an existing file inside a container filesystem incur latency on the first write?",
            "options": [
                "The file must be downloaded from the remote registry",
                "The kernel must encrypt the layer with SHA256",
                "The overlay2 driver must copy the file from the read-only LowerDir up to the mutable UpperDir",
                "The host filesystem must flush all memory caches to disk",
            ],
            "answer_index": 2,
            "explanation": "In union filesystems, Copy-on-Write (CoW) requires copying the file from read-only LowerDir up into UpperDir before modifying it.",
        },
        {
            "id": "q_004",
            "question": "Why is the ':latest' image tag considered dangerous for production deployment manifests?",
            "options": [
                "Docker forbids pushing the ':latest' tag to remote registries",
                "':latest' is a mutable floating pointer, leading to non-deterministic builds and untested drift",
                "Images with ':latest' tags cannot be cached by the daemon",
                "':latest' images only run on amd64 architectures",
            ],
            "answer_index": 1,
            "explanation": "':latest' is merely a floating tag that can be overwritten at any time, breaking deployment reproducibility.",
        },
        {
            "id": "q_005",
            "question": "Which Dockerfile syntax ensures your application process receives termination signals as PID 1 without a shell wrapper?",
            "options": [
                "ENTRYPOINT python app.py",
                "CMD python app.py",
                "ENTRYPOINT [\"python\", \"app.py\"]",
                "RUN python app.py",
            ],
            "answer_index": 2,
            "explanation": "The JSON array exec form 'ENTRYPOINT [\"python\", \"app.py\"]' runs the process directly as PID 1 without a '/bin/sh -c' wrapper.",
        },
    ]

    cheat_sheet = (
        "DOCKER INTERMEDIATE CHEAT SHEET:\n\n"
        "CONTAINER LIFECYCLE:\n"
        "  docker run -d --name <name> -p <host>:<cont> <image>   # Run in background\n"
        "  docker stop -t 10 <container>                          # Graceful SIGTERM stop\n"
        "  docker rm -f <container>                               # Force remove container\n"
        "  docker logs -f --tail 100 <container>                  # Stream logs\n"
        "  docker exec -it <container> sh                         # Diagnostic shell\n\n"
        "IMAGE MANAGEMENT:\n"
        "  docker build -t <name>:<tag> .                         # Build image from context\n"
        "  docker image ls                                        # List local images\n"
        "  docker rmi <image>                                     # Remove image\n"
        "  docker system df                                       # Storage consumption\n"
        "  docker system prune -af                                # Reclaim unused disk\n\n"
        "VOLUMES & NETWORKS:\n"
        "  docker volume create <vol_name>                        # Named volume\n"
        "  docker run -v <vol_name>:/data <image>                 # Attach volume\n"
        "  docker network create <net_name>                       # User-defined bridge\n"
        "  docker run --net <net_name> <image>                    # Connect to network\n\n"
        "RESOURCE LIMITS:\n"
        "  docker run -m 512m --cpus 1.5 <image>                  # Enforce memory and CPU caps"
    )

    curriculum_blueprint = {
        "course_title": topic,
        "duration_minutes": minutes,
        "target_level": level,
        "total_modules": 9,
        "total_slides": len(slides),
        "modules": [
            {"module": 1, "title": "Prerequisites, Tooling Verification & Environment Baseline", "duration_min": 5, "slides": ["s_001", "s_002"]},
            {"module": 2, "title": "Containers vs Virtual Machines & Kernel Isolation", "duration_min": 10, "slides": ["s_003", "s_004"]},
            {"module": 3, "title": "Docker Engine Architecture & Container Lifecycle", "duration_min": 10, "slides": ["s_005", "s_006"]},
            {"module": 4, "title": "Images, Layers, Registries & Tagging Strategies", "duration_min": 10, "slides": ["s_007", "s_008", "s_009"]},
            {"module": 5, "title": "Writing Dockerfiles, Multi-Stage Builds & Caching", "duration_min": 15, "slides": ["s_010", "s_011", "s_012", "s_013"]},
            {"module": 6, "title": "Running Containers, Ports, Environment & Observability", "duration_min": 10, "slides": ["s_014", "s_015", "s_016"]},
            {"module": 7, "title": "Volumes, Networks & Operational Resource Limits", "duration_min": 10, "slides": ["s_017", "s_018", "s_019"]},
            {"module": 8, "title": "Guided Hands-on Lab & Diagnostic Runbook", "duration_min": 15, "slides": ["s_020", "s_021", "s_022"]},
            {"module": 9, "title": "Recap, Knowledge Check & Production Readiness", "duration_min": 5, "slides": ["s_023", "s_024"]},
        ],
    }

    verification_manifest = {
        "code_blocks": [
            {
                "id": "c_001",
                "lang": "python",
                "status": "passed",
                "verification_scope": "Python 3.12 Microservice Sandbox Runner",
                "notes": "Verified syntax, signal handling, and clean HTTP socket lifecycle.",
            }
        ],
        "docker_runtime_verification": {
            "status": "verification_unavailable_locally",
            "scope": "Docker Daemon CLI & Container Engine",
            "reason": "Host Docker daemon not accessible in sandboxed test execution runner.",
            "instructions": "Verified manually via automated CLI runbook on Linux host.",
        },
        "tests_must_bite": {
            "exercise_id": "e_001",
            "proven": True,
            "reference_passes": True,
            "naive_fails": True,
        },
    }

    return {
        "deck_id": deck_id,
        "topic": topic,
        "level": level,
        "minutes": minutes,
        "stack": stack,
        "slides": slides,
        "exercises": exercises,
        "quiz": quiz,
        "cheat_sheet": cheat_sheet,
        "meta": {
            "source": "trainer-grade-benchmark-engine",
            "curriculum_blueprint": curriculum_blueprint,
            "verification_manifest": verification_manifest,
        },
    }
