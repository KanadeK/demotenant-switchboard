# Release Checklist

- Confirm `gh auth status` is logged in as `KanadeK`.
- Confirm `gh api user --jq '{login: .login, id: .id}'`.
- Configure local Git author as `KanadeK <121669563+KanadeK@users.noreply.github.com>`.
- Run `python -m pip install -e ".[dev]"`.
- Run `python scripts/verify.py`.
- Run `python scripts/demo.py`.
- Run `python scripts/package_release.py`.
- Commit release artifacts.
- Run `python scripts/release_check.py`.
- Confirm `git log --all --format="%H | Author: %an <%ae> | Committer: %cn <%ce>%n%B%n---"` has no foreign author or co-author.
- Push `main` without force.
- Watch CI and Pages until success.
- Create `v0.1.0` only after all checks pass.
- Verify release tag SHA matches latest `main` SHA.
- Verify remote commits and contributors show only `KanadeK`.
