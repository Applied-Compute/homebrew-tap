# Applied Compute Homebrew tap

Install the Shift CLI on macOS or Linux (Apple Silicon/ARM64 or Intel/AMD64).
You need [Homebrew](https://brew.sh), but no Relay checkout, Go compiler, or GitHub credentials.

```sh
brew install Applied-Compute/tap/acshift
acshift install
```

**Bootstrap status:** the initial `acshift-v2026.10.19.1` GitHub release must be
published using the workflow below before the install command works.

Homebrew installs the CLI and prints the setup command. It does not run setup,
request credentials, change agent configuration, or edit your shell profile.
`acshift install` performs the interactive connection flow.

To use the short package name, add the tap first:

```sh
brew tap Applied-Compute/tap
brew install acshift
```

## Upgrades and removal

```sh
brew update
brew upgrade Applied-Compute/tap/acshift
```

The launcher pins `SHIFT_RELEASE_URL` to the installed release, overriding any
shell value. The current CLI checks for updates during setup by comparing binary
bytes; pinning that URL prevents it from replacing a Homebrew-managed executable.
It still downloads its pinned bundle during that check, so setup requires network
access. This wrapper can be removed once the CLI supports package-manager-owned
updates directly. The installed binary itself is unchanged.

To disconnect agents, run `acshift uninstall` before `brew uninstall acshift`.
Homebrew removal alone removes the package, not your agent configuration.
If you previously used the shell installer, check `which -a acshift`: an old
`~/.local/bin/acshift` earlier on PATH may shadow the Homebrew command. Remove that
old executable when migrating; do not delete your Shift configuration.

## First publication

The formula pins the four publicly served bundles captured from
`https://shift.ac/downloads/cli`. `release.json` records archive SHA-256 values and
the expected CLI build ID. Package versions use `YYYY.MM.DD.N` and increase for
each publication; `acshift --version` continues to report the upstream build ID.
No private Relay source is copied into this repository.

1. Merge the initialization PR.
2. In GitHub Actions, run **Publish pinned acshift release** on `main`:
   ```sh
   gh workflow run publish.yml --repo Applied-Compute/homebrew-tap --ref main
   ```
3. Wait for the four-platform installation tests and publishing job to succeed.
4. Verify from a fresh Homebrew installation:
   ```sh
   brew install Applied-Compute/tap/acshift
   acshift --version
   acshift install
   ```

The workflow uses the repository's `GITHUB_TOKEN` with `contents: write`; no Relay
access token or other secret is needed. Repository/organization policy must allow
GitHub Actions and the pinned checkout and Homebrew setup actions. Only `main`
can publish. Publishing is manual and never happens on a PR or ordinary push.

The workflow stages all assets in a draft release before making it public. It
never overwrites an existing release. If publication fails after creating a draft,
inspect the draft and complete or delete it deliberately before retrying. Enable
GitHub release immutability in repository settings where available; never replace
published bundles in place.

If the website deploys different bundles before publication, checksum validation
fails closed. Prepare a new snapshot below, or recover the exact reviewed bundles
from the corresponding Relay build artifacts; do not bypass checksum verification.
The formula's SHA-256 is for the entire archive, not the binary checksum inside it.

## Preparing the next release

Download all four bundles into an empty directory (or obtain matching bundles
from Relay's build artifacts):

```sh
mkdir -p dist
for platform in darwin-arm64 darwin-amd64 linux-arm64 linux-amd64; do
  curl --fail --location --proto '=https' --proto-redir '=https' \
    --connect-timeout 10 --max-time 120 \
    "https://shift.ac/downloads/cli/acshift-$platform.tar.gz" \
    -o "dist/acshift-$platform.tar.gz"
done
```

Read the expected build ID from the release build, or extract the native binary
and run `--version`. Generate the formula with a new, increasing package version:

```sh
python3 scripts/release.py prepare \
  --version 2026.10.20.1 \
  --build-version ACTUAL_UPSTREAM_BUILD_ID \
  --bundles dist
python3 scripts/release.py check
python3 -m unittest discover -s tests
```

Commit `Formula/acshift.rb` and `release.json` together in a PR. Review the build
ID and checksums, let CI pass, merge, and run the publishing workflow. Preparation
validates each embedded binary checksum and rejects unexpected archive members.
CI executes the CLI on each native architecture to check its build ID and verifies
that the installed binary matches the archive.

## Validation

**Test tap** runs on PRs, pushes to `main`, and manual dispatches. It checks the
manifest/formula agreement and checksum rejection tests, then installs, tests,
and uninstalls the formula on macOS ARM64/AMD64 and Linux ARM64/AMD64. It uses
published bundles when available, falling back to the website only if all bytes
match the reviewed checksums. To validate before publication, CI changes only the
download URLs in its temporary tap clone to local verified files; the launcher
still points at the eventual public release. This tests packaging, not interactive
setup. The final fresh-machine check after publication covers public URL access
and the interactive setup flow.
