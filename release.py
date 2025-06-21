import subprocess
import datetime
import argparse
import re
from pathlib import Path

CHANGELOG_PATH = "CHANGELOG.md"
PYPROJECT_PATH = "pyproject.toml"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--hotfix", action="store_true", help="Create a hotfix without incrementing version")
    parser.add_argument("--patch", action="store_true", help="Increment patch version")
    parser.add_argument("--tag", type=str, help="Version tag to append (e.g., dev, beta)")
    parser.add_argument("--no-tag", action="store_true", help="Skip Git tag creation")
    return parser.parse_args()


def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):
                return line.split("=")[1].split("#")[0].strip().strip('"')
    raise RuntimeError("version not found in pyproject.toml")


def compute_next_version(current_version, patch=False, tag=None):
    base, *old_tag = current_version.split("-")
    year, build = base.split(".")
    new_build = int(build) + 1 if patch or not old_tag else int(build)
    suffix = tag or old_tag[0] if old_tag else ""
    return f"{year}.{new_build}-{suffix}" if suffix else f"{year}.{new_build}"


def update_pyproject_version(new_version, dry_run=False):
    content = Path(PYPROJECT_PATH).read_text(encoding="utf-8")
    new_content = re.sub(
        r'version\s*=\s*"[\d\.\-\w]+"',
        f'version = "{new_version}"',
        content
    )
    if dry_run:
        print(f"[DRY-RUN] Would update pyproject.toml to version: {new_version}")
    else:
        Path(PYPROJECT_PATH).write_text(new_content, encoding="utf-8")
        print(f"[release] pyproject.toml updated to version {new_version}")


def get_commits_since_last_tag():
    try:
        last_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], encoding="utf-8").strip()
        range_spec = f"{last_tag}..HEAD"
    except subprocess.CalledProcessError:
        range_spec = "HEAD"
    commits = subprocess.check_output(["git", "log", range_spec, "--pretty=format:%s"], encoding="utf-8")
    return commits.strip().split("\n") if commits else []


def classify_commits(commits):
    added, changed, fixed, other = [], [], [], []
    for c in commits:
        cl = c.lower()
        if cl.startswith("feat:"):
            added.append(c[5:].strip())
        elif cl.startswith("fix:"):
            fixed.append(c[4:].strip())
        elif cl.startswith("change:"):
            changed.append(c[7:].strip())
        else:
            other.append(c.strip())
    return added, changed, fixed, other


def format_changelog(version, added, changed, fixed, other):
    today = datetime.date.today().isoformat()
    def sec(title, lines): return f"### {title}\n" + "\n".join(f"- {l}" for l in lines) + "\n\n" if lines else ""
    return (
        f"\n## [{version}] - {today}\n\n"
        + sec("Added", added)
        + sec("Changed", changed)
        + sec("Fixed", fixed)
        + sec("Other", other)
    )


def insert_changelog_entry(version, block, dry_run=False):
    changelog = Path(CHANGELOG_PATH)
    content = changelog.read_text(encoding="utf-8")
    if f"## [{version}]" in content:
        print(f"[release] Changelog already contains version {version}")
        return
    new_content = block + content
    if dry_run:
        print(f"[DRY-RUN] Would insert changelog entry:\n---\n{block}\n---")
    else:
        changelog.write_text(new_content, encoding="utf-8")
        print(f"[release] Changelog updated with version {version}")


def git_commit_and_tag(version, dry_run=False, no_tag=False):
    if dry_run:
        print(f"[DRY-RUN] Would commit and tag version {version}")
        return

    subprocess.run(["git", "add", PYPROJECT_PATH, CHANGELOG_PATH], check=True)
    subprocess.run(["git", "commit", "-m", f"release: v{version}"], check=True)

    if not no_tag:
        tag = f"v{version}"
        subprocess.run(["git", "tag", tag], check=True)
        print(f"[release] Created Git tag {tag}")


def main():
    args = parse_args()
    dry = args.dry_run
    hotfix = args.hotfix
    patch = args.patch
    tag = args.tag

    current_version = get_current_version()

    if hotfix:
        if current_version.endswith("-hotfix"):
            next_version = current_version
        else:
            next_version = f"{current_version}-hotfix"
    else:
        next_version = compute_next_version(current_version, patch=patch, tag=tag)

    print("======================")
    print(f"[{'DRY-RUN' if dry else 'release'}] Preparing Release")
    print(f"[{'DRY-RUN' if dry else 'release'}]   From: {current_version}")
    print(f"[{'DRY-RUN' if dry else 'release'}]   To:   {next_version}")
    print(f"[{'DRY-RUN' if dry else 'release'}]   Mode: {'Hotfix' if hotfix else 'Patch' if patch else 'Normal'}")
    print(f"[{'DRY-RUN' if dry else 'release'}]   Tag:  {tag or '(none)'}")
    print("======================")
    if input(f"[{'DRY-RUN' if dry else 'release'}] Continue? [y/N]: ").strip().lower() != "y":
        print(f"[{'DRY-RUN' if dry else 'release'}] Aborted.")
        return

    update_pyproject_version(next_version, dry_run=dry)

    commits = get_commits_since_last_tag()
    added, changed, fixed, other = classify_commits(commits)

    block = format_changelog(next_version, added, changed, fixed, other)
    insert_changelog_entry(next_version, block, dry_run=dry)

    if input(f"[{'DRY-RUN' if dry else 'release'}] Proceed with Git staging and tag? [y/N]: ").strip().lower() == "y":
        git_commit_and_tag(next_version, dry_run=dry, no_tag=args.no_tag)


if __name__ == "__main__":
    main()
