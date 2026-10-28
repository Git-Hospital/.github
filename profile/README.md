<img src="https://raw.githubusercontent.com/Git-Hospital/.github/main/profile/assets/hospital.svg" width="100%" alt="Git Hospital at night: a hospital with a neon GIT HOSPITAL sign on the roof, lit wards and an ambulance arriving at the emergency entrance. Open-source tools that diagnose infrastructure and code.">

<p align="center">
  <b>We diagnose Helm charts, service meshes and codebases, and show the evidence for every finding.</b><br>
  <sub><a href="#triage-desk">Triage desk</a> · <a href="#wards">Wards</a> · <a href="#case-board">Case board</a> · <a href="#quick-start">Quick start</a> · <a href="#house-rules">House rules</a> · <a href="#staff">Staff</a></sub>
</p>

<img src="https://raw.githubusercontent.com/Git-Hospital/.github/main/profile/assets/pathway.svg" width="100%" alt="Patient pathway, from a symptom to a fix you can review: symptom, triage, diagnosis (Helmbulance, MeshMedic, GitHealthCheck), evidence (Markdown, JSON, SARIF), treatment (MeshMedic, Helmbulance), second opinion (boards).">

## Triage desk

Tell us the symptom, we send you to the right ward.

| Symptom | Ward | Treatment | Status |
| --- | --- | --- | --- |
| *"The chart installed fine. The upgrade, the reinstall or the Secret rotation broke it."* | Emergency · [Helmbulance](https://github.com/Git-Hospital/helmbulance) | Installs the chart on a throwaway kind cluster and replays day-2 scenarios. A finding is reported when it reproduces on the cluster. | Pre-release; v0.1 planned for 8 November 2026 |
| *"Istio is throwing 503s and nobody knows which policy did it."* | Intensive care · [MeshMedic](https://github.com/Git-Hospital/meshmedic) | Reads Istio's Prometheus telemetry, matches a human-reviewed catalog of failure scenarios and opens a GitOps pull request with the diagnosis, the evidence and a rollback plan. No LLM, no writes to the cluster. | v1.0.0 |
| *"Our diagnosis tool says it works. Does it?"* | Clinical trials · [boards](https://github.com/Git-Hospital/boards) | A benchmark of known defects, clean twins and hand-verified values that scores what a tool finds and whether its fix works once applied. One track today: eleven Istio ambient incidents. | In development |
| *"How healthy is this repository, really?"* | Check-up · [GitHealthCheck](https://github.com/Git-Hospital/githealthcheck) | A code health analyzer for tests, history and complexity, where every number is a measurement or null with the reason it could not be measured. Go and Python are analysed. | v0.3.0 |

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

## Case board

<a href="https://github.com/Git-Hospital/helmbulance#found-in-public-charts"><img src="https://raw.githubusercontent.com/Git-Hospital/.github/vitals/cases.svg" width="100%" alt="Case board: bugs that Helmbulance found or reproduced in public Helm charts, with the live status of each upstream issue and fix."></a>

<sub>The board is live too: each status is read from the upstream issue and pull request every morning.
<b>FIXED</b>: the fix is merged. <b>FIX APPROVED</b>: a maintainer approved it. <b>FIX IN REVIEW</b>: a fix is open.
<b>REPORTED</b>: the issue is open with no fix yet. <b>check in review</b>: the Helmbulance check that finds it is not merged yet.</sub>

<details>
<summary><b>The cases, with links</b></summary>

| Chart | What broke | Found by | Upstream |
| --- | --- | --- | --- |
| SeaweedFS | The first upgrade after install restarts the filer and the S3 gateway | `upgrade-without-values` (HB-UV-003) | [#11719](https://github.com/seaweedfs/seaweedfs/issues/11719), fix [#11720](https://github.com/seaweedfs/seaweedfs/pull/11720) |
| JupyterHub | The same restart, for the hub and the proxy | `upgrade-without-values` (HB-UV-003) | [#3996](https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues/3996), fix [#3997](https://github.com/jupyterhub/zero-to-jupyterhub-k8s/pull/3997) |
| Semaphore | The same restart | `upgrade-without-values` (HB-UV-003) | [#34](https://github.com/semaphoreui/charts/issues/34), fix [#35](https://github.com/semaphoreui/charts/pull/35) |
| yugabyte | Patch release 2026.1.2 changes a StatefulSet selector, so upgrades from 2026.1.0 and 2026.1.1 fail | `scan`, confirmed by `chart-upgrade` (HB-CU-001) | [#240](https://github.com/yugabyte/charts/issues/240) |
| SeaweedFS | An unquoted number or boolean in `extraEnvironmentVars` fails the install | `scan` (HB-SCAN-004) | fix [#12137](https://github.com/seaweedfs/seaweedfs/pull/12137) |
| SeaweedFS | With the MySQL filer store, a reinstall writes a new database password | `reinstall` (HB-RI-004) | fix [#12138](https://github.com/seaweedfs/seaweedfs/pull/12138) |
| Jenkins | Without cluster access the admin password is new on every render, so Argo CD replaces it on every sync | `gitops-render` (HB-GR-001) | [#1026](https://github.com/jenkinsci/helm-charts/issues/1026), reported by others |
| docker-registry | `haSharedSecret` changes on every upgrade | `upgrade-without-values` (HB-UV-001) | [#187](https://github.com/twuni/docker-registry.helm/issues/187), reported by others |
| docker-registry-ui | The app version in the Deployment selector breaks every upgrade that changes it | `scan` (HB-SCAN-001) | fix [#22](https://github.com/Joxit/helm-charts/pull/22) by others, verified with Helmbulance |
| grafana 6.9.2 | The admin password changes on every upgrade | `upgrade-without-values` (HB-UV-001) | [#10](https://github.com/grafana/helm-charts/issues/10), fix [#62](https://github.com/grafana/helm-charts/pull/62), reported by others |

</details>

## Quick start

<details>
<summary><b>Helmbulance</b>: test a Helm chart's day two (needs Go; <code>test</code> also needs Docker, kind and helm)</summary>

```sh
git clone https://github.com/Git-Hospital/helmbulance && cd helmbulance
go build -o bin/helmbulance ./cmd/helmbulance
./bin/helmbulance scan ./path/to/chart                    # static pre-screen, no cluster
./bin/helmbulance test ./path/to/chart -f values.yaml     # scenarios on a throwaway kind cluster
```

Run `test` only on charts you trust: it installs them on your Docker host.
</details>

<details>
<summary><b>MeshMedic</b>: watch an Istio service against the Prometheus you already run</summary>

```sh
docker run --rm --network host ghcr.io/kassvl/meshmedic:latest \
  watch --prometheus http://localhost:9090 \
        --target service=payments,namespace=demo
```
</details>

<details>
<summary><b>GitHealthCheck</b>: scan a repository (needs git 2.44 or later)</summary>

```sh
go install github.com/Git-Hospital/githealthcheck/cmd/githealthcheck@latest
githealthcheck scan .
```
</details>

<details>
<summary><b>boards</b>: run the benchmark without a cluster</summary>

```sh
git clone https://github.com/Git-Hospital/boards && cd boards
go build -o boards ./cmd/boards
./boards run --adapter adapters/dummy/oracle --dry-run
```
</details>

## House rules

- **No diagnosis without evidence.** A tool shows what it measured and how it got to the finding.
- **"Could not check" is not "healthy".** When a tool cannot look, it says so.
- **Second opinions welcome.** Benchmarks, fixtures and demos can be rerun by anyone, misses included.
- **Every procedure is reviewed.** Changes land through pull requests with green CI.

## Admissions

Issues and pull requests are welcome in every ward. Read the repository's `CONTRIBUTING.md` first.
Security problems go to the isolation ward: the **Report a vulnerability** button on the repository's Security tab, not a public issue.

## Staff

<table>
  <tr>
    <td align="center"><a href="https://github.com/kassvl"><img src="https://github.com/kassvl.png?size=120" width="64" alt=""><br><b>Kadirhan Emre</b></a><br><sub>MeshMedic, boards, GitHealthCheck<br>Helmbulance CI and Action</sub></td>
    <td align="center"><a href="https://github.com/egezamb"><img src="https://github.com/egezamb.png?size=120" width="64" alt=""><br><b>Ege Zambelli</b></a><br><sub>Helmbulance CLI and scenarios<br>upstream reports</sub></td>
  </tr>
</table>
