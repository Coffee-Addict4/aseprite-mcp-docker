Model Stability & Speed Optimization Rules for MCP Tools
1. Strict Modularity
- Isolate systems by responsibility. No deep cross-system dependencies.
- Interface via event hooks or clean APIs. Avoid shared memory states.
2. Dependency Discipline
- Use only essential third-party libraries with performance justification.
- Prefer raw asset formats and native features over bloated abstractions.
- Avoid complex frameworks unless they solve multiple problems efficiently.
3. Fail-Safe Defaults
- Default settings favor safety: reduced resource usage, low-resolution loadouts, and graceful fallback behavior.
- Use null handlers or fallback shaders for missing resources.
- Avoid runtime assumptions — validate inputs upfront.
4. Immutable Core Config
- Lock config files as readonly after boot — especially global logic and render parameters.
- Permit local overrides only in safe sandboxes.
- External tools should version and approve any structural edits.
5. Async Discipline
- Bound all async operations with timeouts and retry limits.
- Use fixed thread pools and avoid recursive task chains.
- Isolate high-cost tasks to separate queues from core logic.
6. Logging, Not Nagging
- Log only critical state changes and threshold breaches.
- Filter logs by severity and system origin (e.g. [ASSET], [RENDER]).
- Snapshot runtime states periodically instead of frame-by-frame verbosity.
7. Watchdog Systems
- Monitor frame delta, memory pressure, asset queue depth.
- Auto-throttle or purge systems upon breach.
- Watchdogs run in parallel with low overhead and visible alerts.
8. Update Immunity
- MCP versions and plugins pinned per project.
- No background updates or auto-patches in production.
- Allow updates only via approved staging systems with rollback support.
9. Micro-Load Strategy
- Stream assets based on proximity or system priority.
- Lazy-init modules; defer load until usage is confirmed.
10. Asset Optimization
- Compress textures (BC7/DXT5) and reduce mesh complexity.
- Consolidate assets via atlasing to cut draw calls.
- Strip debug components and non-visible elements from builds.
11. Render Pass Efficiency
- Enable frustum/occlusion/shader pass culling.
- Pre-bake lighting when viable.
- Use depth pre-pass to reduce overdraw.
12. Scripting Hotpaths
- Profile logic paths aggressively for cost and frequency.
- Avoid memory allocation mid-frame; reuse buffers.
- Move high-load logic to native MCP scripts or extensions.
13. Fast Dev Loops
- Use proxy assets and debug shaders for quick iteration.
- Preview scenes with simplified lighting and physics.
- Overlay real-time frame cost indicators during editing.
14. Parallelism & Task Batching
- Batch resource I/O and simulation passes.
- Run on fixed thread pools with shared-state protection.
- Offload to GPU compute where supported.
15. Minimal UI Overhead
- Separate UI rendering from gameplay rendering.
- Flatten layout trees and cache expensive UI logic.
- Run animation and input handling outside core frame tick.
16. Cooldown Throttling
- Align interaction cooldowns with frame budget, not wall time.
- Cap repetitive system triggers (buffs, fountains) per tick.
- Use throttle queues to buffer load surges.


17. Instruction Integrity Lock
- Core instruction sets must be readonly at runtime.
- No reflection, dynamic patching, or recursive overwrite.
- Structural edits only allowed via external versioned tooling.
