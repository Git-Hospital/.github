# Git Hospital

Open source tools that diagnose infrastructure and code, and show the evidence for every diagnosis.

Each tool here follows the same rule: a finding is only reported when the tool can show how it got there. If it could not look, it says so instead of reporting "healthy".

## Tools

| Tool | What it does | Status |
| --- | --- | --- |
| [MeshMedic](https://github.com/Git-Hospital/meshmedic) | Watches Istio's Prometheus telemetry, matches a human-reviewed catalog of failure scenarios, and opens a GitOps pull request with the diagnosis, evidence and rollback plan. No LLM, no cluster writes. | v1.0.0 |
| [mesh-incidents-bench](https://github.com/Git-Hospital/mesh-incidents-bench) | 11 reproducible service mesh failure scenarios with ground truth, for scoring diagnostic and remediation tools. Misses are published, including our own. | scenarios and results |
| [GitHealthCheck](https://github.com/Git-Hospital/githealthcheck) | Code health analyzer for Git repositories: tests, history, complexity, architecture. Every number is a measurement, or null with a reason. | Go rewrite in progress |

## How we work

- **Evidence or silence.** A tool reports what it measured. "Could not check" is a separate answer from "nothing wrong".
- **Reproducible claims.** Benchmarks, fixtures and demos can be rerun by anyone. Results include the cases where our tools lose.
- **Changes through pull requests.** New changes land through a pull request with green CI.

## Contributing

Issues and pull requests are welcome in every repository. Read the repository's `CONTRIBUTING.md` first. To report a vulnerability privately, use the "Report a vulnerability" button on the repository's Security tab.
