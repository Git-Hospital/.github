<img src="https://raw.githubusercontent.com/Git-Hospital/.github/main/profile/assets/hospital.svg" width="100%" alt="Git Hospital at night: a hospital with a neon GIT HOSPITAL sign on the roof, lit wards and an ambulance arriving at the emergency entrance. Open-source tools that diagnose infrastructure and code.">

## Triage desk

Tell us the symptom, we send you to the right ward.

| Symptom | Ward | Treatment |
| --- | --- | --- |
| *"The chart installed fine. The upgrade, the reinstall or the Secret rotation broke it."* | Emergency · [Helmbulance](https://github.com/Git-Hospital/helmbulance) | Installs the chart on a throwaway kind cluster and replays day-2 scenarios. A finding is reported when it reproduces on the cluster. |
| *"Istio is throwing 503s and nobody knows which policy did it."* | Intensive care · [MeshMedic](https://github.com/Git-Hospital/meshmedic) | Reads Istio's Prometheus telemetry, matches a human-reviewed catalog of failure scenarios and opens a GitOps pull request with the diagnosis, the evidence and a rollback plan. No LLM, no writes to the cluster. |
| *"Our diagnosis tool says it works. Does it?"* | Clinical trials · [boards](https://github.com/Git-Hospital/boards) | In development: a benchmark of known defects, clean twins and hand-verified values that scores what a tool finds and whether its fix works once applied. |
| *"How healthy is this repository, really?"* | Check-up · [GitHealthCheck](https://github.com/Git-Hospital/githealthcheck) | A code health analyzer for tests, history and complexity (Go today, v0.2.0), where every number is a measurement or null with the reason it could not be measured. |

## Wards

<table>
  <tr>
    <td width="50%"><a href="https://github.com/Git-Hospital/helmbulance"><img src="https://raw.githubusercontent.com/Git-Hospital/.github/vitals/helmbulance.svg" width="100%" alt="Patient monitor for Helmbulance"></a></td>
    <td width="50%"><a href="https://github.com/Git-Hospital/meshmedic"><img src="https://raw.githubusercontent.com/Git-Hospital/.github/vitals/meshmedic.svg" width="100%" alt="Patient monitor for MeshMedic"></a></td>
  </tr>
  <tr>
    <td width="50%"><a href="https://github.com/Git-Hospital/boards"><img src="https://raw.githubusercontent.com/Git-Hospital/.github/vitals/boards.svg" width="100%" alt="Patient monitor for boards"></a></td>
    <td width="50%"><a href="https://github.com/Git-Hospital/githealthcheck"><img src="https://raw.githubusercontent.com/Git-Hospital/.github/vitals/githealthcheck.svg" width="100%" alt="Patient monitor for GitHealthCheck"></a></td>
  </tr>
</table>

<sub>The monitors are live. A workflow reads the GitHub API every morning and redraws them.
<b>Pulse</b> is the number of commits on the default branch in the last 90 days; the trace goes flat when there are none.
<b>Checks</b> are the GitHub check runs on the latest commit (cancelled runs are left out).
<b>STABLE</b>: checks pass. <b>CRITICAL</b>: a check failed. <b>PENDING</b>: checks still running.
<b>NO CHECKS</b>: nothing ran, so the monitor cannot tell. <b>DORMANT</b>: no commit in 90 days.</sub>

## House rules

- **No diagnosis without evidence.** A tool shows what it measured and how it got to the finding.
- **"Could not check" is not "healthy".** When a tool cannot look, it says so.
- **Second opinions welcome.** Benchmarks, fixtures and demos can be rerun by anyone, misses included.
- **Every procedure is reviewed.** Changes land through pull requests with green CI.

## Admissions

Issues and pull requests are welcome in every ward. Read the repository's `CONTRIBUTING.md` first.
Security problems go to the isolation ward: the **Report a vulnerability** button on the repository's Security tab, not a public issue.
