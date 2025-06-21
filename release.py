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
    parser.add_argument("--hotfix", action="store_true", help="Tag a hotfix (does not increment version)")
    parser.add_argument("--patch", action="store_true", help="Optional patch bump (overrides default)")
    parser.add_argument("--tag", type=str, help="Optional version tag (e.g., dev, beta, stable)")
    parser.add_argument("--no-tag", action="store_true", help="Skip Git tagging")
    return parser.parse_args()

def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):
                return line.split("=")[1].split("#")[0].strip().strip('"')
    raise RuntimeError("version not found in pyproject.toml")

def compute_next_version(current_version, patch=True, hotfix=False, tag=None):
    base_version = current_version.split("-")[0]
    current_tag = current_version[len(base_version):].lstrip("-")
    year, build = base_version.split(".")
    if patch and not hotfix:
        build = str(int(build) + 1)
    next_version = f"{year}.{build}"

    if tag and tag != current_tag:
        next_version += f"-{tag}"
    elif current_tag:
        next_version += f"-{current_tag}"
    return next_version

def update_pyproject_version(new_version, dry_run=False):
    content = Path(PYPROJECT_PATH).read_text(encoding="utf-8")
    new_content = re.sub(
        r'version\s*=\s*"[\d\.]+-[\w]+"',
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
    content = Path(CHANGELOG_PATH).read_text(encoding="utf-8")
    if f"## [{version}]" in content:
        print(f"[release] Changelog already contains version {version}")
        return
    new_content = block + content
    if dry_run:
        print(f"[DRY-RUN] Would insert changelog entry:\n---\n{block}\n---")
    else:
        Path(CHANGELOG_PATH).write_text(new_content, encoding="utf-8")
        print(f"[release] Changelog updated with version {version}")

def git_commit_and_tag(version, dry_run=False, no_tag=False):
    if dry_run:
        print(f"[DRY-RUN] Would commit and tag version {version}")
        return

    # STAGING PROMPT
    proceed = input("[STAGING] Proceed with commit and tag? [y/N]: ").strip().lower()
    if proceed != "y":
        print("[STAGING] Aborted before commit/tag.")
        return

    subprocess.run(["git", "add", PYPROJECT_PATH, CHANGELOG_PATH], check=True)
    subprocess.run(["git", "commit", "-m", f"release: v{version}"], check=True)

    if no_tag:
        print(f"[release] Skipping tag for v{version}")
        return

    tag = f"v{version}"
    result = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)
    if tag in result.stdout:
        print(f"[release] Tag {tag} already exists, deleting...")
        subprocess.run(["git", "tag", "-d", tag], check=True)

    subprocess.run(["git", "tag", tag], check=True)
    print(f"[release] Created commit and tag {tag}")

def prompt_continue_summary(current_version, new_version, args):
    prefix = "[DRY-RUN] " if args.dry_run else ""
    print("======================")
    print(f"{prefix}Preparing Release")
    print(f"{prefix}  From: {current_version}")
    print(f"{prefix}  To:   {new_version}")
    print(f"{prefix}  Mode: {'Hotfix' if args.hotfix else 'Patch' if args.patch else 'Normal'}")
    print(f"{prefix}  Tag:  {args.tag or 'inferred'}")
    print(f"{prefix}  Git Tagging: {'Skipped' if args.no_tag else 'Enabled'}")
    print("======================")
    proceed = input(f"{prefix}Continue? [y/N]: ").strip().lower()
    if proceed != "y":
        print(f"{prefix}Aborted.")
        exit(0)

def main():
    args = parse_args()
    current_version = get_current_version()
    tag = args.tag or "dev"

    next_version = compute_next_version(
        current_version,
        patch=args.patch or not args.hotfix,
        hotfix=args.hotfix,
        tag=tag
    )

    prompt_continue_summary(current_version, next_version, args)
    update_pyproject_version(next_version, dry_run=args.dry_run)

    commits = get_commits_since_last_tag()
    added, changed, fixed, other = classify_commits(commits)
    block = format_changelog(next_version, added, changed, fixed, other)
    insert_changelog_entry(next_version, block, dry_run=args.dry_run)
    git_commit_and_tag(next_version, dry_run=args.dry_run, no_tag=args.no_tag)

if __name__ == "__main__":
    main()
