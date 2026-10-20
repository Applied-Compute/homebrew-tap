# Applied Compute Homebrew tap

This repository hosts the Shift Homebrew formula and public release binaries.
Relay owns building, testing, and publishing those binaries and opening formula
update PRs. No Relay source or private repository access is needed to install.

**Bootstrap status:** merge this tap's initialization PR, then run Relay's
**Release acshift for Homebrew** workflow on `main`. That publishes the first
release and opens a PR adding `Formula/acshift.rb` and `release.json` here. Merge
that generated PR before advertising the commands below. There is deliberately
no formula pointing to an unpublished release.

## Install

With [Homebrew](https://brew.sh) installed:

```sh
brew install Applied-Compute/tap/acshift
acshift install
```

Supported platforms: macOS and Linux, ARM64 and AMD64. Homebrew downloads a
prebuilt binary; no Relay checkout, Go compiler, or GitHub credentials are needed.
It prints the setup command without running setup, requesting credentials,
changing agent configuration, or editing shell profiles.

For the short package name, first run `brew tap Applied-Compute/tap`, then
`brew install acshift`.

## Upgrade and remove

```sh
brew update
brew upgrade Applied-Compute/tap/acshift
```

The launcher's `SHIFT_RELEASE_URL` points to the installed release and overrides
any shell value. The CLI compares its binary with that pinned bundle when checking
for updates, preventing it from replacing the Homebrew-managed executable with
the website's latest version. This check still needs network access. The wrapper
can be removed when the CLI supports package-manager-owned updates directly.

To disconnect agents, run `acshift uninstall` before `brew uninstall acshift`.
Homebrew removal alone does not remove agent configuration. If migrating from the
shell installer, check `which -a acshift`: an old `~/.local/bin/acshift` may shadow
Homebrew. Remove that old executable when migrating, not your Shift configuration.

## Releases and maintenance

Release maintainers use Relay's **Release acshift for Homebrew** workflow with an
increasing package version, such as `2026.10.20.1`. It builds from the dispatched
`main` commit using Relay's bundling script, tests the exact bundles through
Homebrew on all four native platforms, uploads them to a versioned GitHub Release
in this repository, and opens a PR updating the formula and manifest. The source
commit remains the build ID reported by `acshift --version`.

Configure `HOMEBREW_TAP_TOKEN` in Relay as described in Relay's `cli/README.md`.
It needs access only to this repository with Contents and Pull requests read/write.
No publishing credentials or publishing workflow belong in this tap. Ordinary
Relay PRs run packaging checks without publishing or using this credential.

Review and merge the generated formula PR after this repository's tests pass.
Updates download only published, versioned release URLs with fixed SHA-256
checksums. There is no fallback to mutable website downloads. Never replace
published release assets; publish a new version. Enable GitHub release immutability
in repository settings where available.

The workflow publishes binaries before opening the formula PR, so merging it
makes the new package available immediately. If opening a PR fails after publishing,
recover the formula and manifest from that Relay run's `acshift-homebrew` artifact
and open the PR manually. Do not republish or overwrite the release.

## Checks

**Test tap** runs on PRs and pushes to `main`. Once the first formula exists, it
installs, tests, and uninstalls the real public release on macOS/Linux × ARM64/AMD64.
Homebrew verifies the archive checksum and the formula checks the CLI build ID and
its unconfigured `doctor` behavior. These checks do not perform interactive setup.
Before the first generated formula PR, metadata validation passes and installation
jobs explicitly skip.
