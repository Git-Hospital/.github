# Contributing

This guide applies to every Git Hospital repository that does not have its own `CONTRIBUTING.md`. If a repository has one, that file wins.

## Before you start

- For anything larger than a typo, open an issue first and describe the problem. That saves you from writing a change that does not fit.
- Security problems go through private vulnerability reporting, not issues. See `SECURITY.md`.

## Pull requests

- One change per pull request, on a branch of your fork.
- CI must pass. Run the repository's tests locally before pushing.
- A bug fix comes with a test that fails without it. A new check or finding comes with a case where it fires and a case where it must not.
- Describe what you changed, why, and how you verified it. If you could not verify something, say so.
- Write the pull request title in the imperative ("Add ...", "Fix ..."). It usually becomes the commit message.

## Claims

The tools here report evidence, so the documentation does too. Numbers in a README, a benchmark or a pull request must come from a run someone can repeat. Do not add a metric, comparison or result you have not measured.

## License

By contributing you agree that your contribution is licensed under the repository's license.
