import subprocess
import datetime
import argparse
import re
from pathlib import Path

PYPROJECT_PATH = "pyproject.toml"
CHANGELOG_PATH = "CHANGELOG.md"

def parse_args():
    parser = argparse.ArgumentParser(description="Release tool for Astral Engine")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to disk")
    parser.add_argument("--hotfix", action="store_true", help="Create a hotfix release (does not bump version)")
    parser.add_argument("--patch", action="store_true", help="Create a patch release (bumps build number)")
    parser.add_argument("--tag", type=str, help="Set tag suffix (e.g., dev, beta, stable)")
    parser.add_argument("--no-tag", action="store_true", help="Skip Git tagging and staging")
    return parser.parse_args()

def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"')
    raise RuntimeError("Version not found in pyproject.toml")

def compute_next_version(current_version, patch=False, tag=None):
    base, *old_tag = current_version.split("-")
    year, build = base.split(".")
    new_build = int(build) + 1 if patch or tag else int(build)

    suffix = tag or (old_tag[0] if old_tag else "")
    return f"{year}.{new_build}-{suffix}" if suffix else f"{year}.{new_build}"

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

def get_commits_since_last_tag():
    try:
        last_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], encoding="utf-8").strip()
        range_spec = f"{last_tag}..HEAD"
    except subprocess.CalledProcessError:
        range_spec = "HEAD"
    commits = subprocess.check_output(["git", "log", range_spec, "--pretty=format:%s"], encoding="utf-8")
    return commits.strip().split("\n") if commits.strip() else []

def format_changelog(version, added, changed, fixed, other, hotfix=False):
    today = datetime.date.today().isoformat()
    heading = f"\n## [{version}] - {today}\n"
    if hotfix:
        heading += f"\n#### Hotfix patch ({today})\n"
    def sec(title, lines): return f"### {title}\n" + "\n".join(f"- {l}" for l in lines) + "\n\n" if lines else ""
    return heading + sec("Added", added) + sec("Changed", changed) + sec("Fixed", fixed) + sec("Other", other)

def insert_changelog_entry(version, block, hotfix=False, dry_run=False):
    content = Path(CHANGELOG_PATH).read_text(encoding="utf-8")
    if hotfix:
        # Add new block with hotfix header at the top
        new_content = block + content
    else:
        if f"## [{version}]" in content:
            print(f"[release] Changelog already contains version {version}")
            return
        new_content = block + content

    if dry_run:
        print(f"[DRY-RUN] Would write changelog:\n---\n{block}\n---")
    else:
        Path(CHANGELOG_PATH).write_text(new_content, encoding="utf-8")
        print(f"[release] Changelog updated with version {version}")

def update_pyproject_version(new_version, dry_run=False):
    content = Path(PYPROJECT_PATH).read_text(encoding="utf-8")
    new_content = re.sub(
        r'version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content
    )
    if dry_run:
        print(f"[DRY-RUN] Would update pyproject.toml to version: {new_version}")
    else:
        Path(PYPROJECT_PATH).write_text(new_content, encoding="utf-8")
        print(f"[release] pyproject.toml updated to version {new_version}")

def git_commit_and_tag(version, dry_run=False, no_tag=False):
    if dry_run:
        print(f"[DRY-RUN] Would commit and tag version {version}")
        return

    subprocess.run(["git", "add", "pyproject.toml", "CHANGELOG.md"], check=True)
    subprocess.run(["git", "commit", "-m", f"release: v{version}"], check=True)

    if no_tag:
        print("[release] Skipping Git tagging due to --no-tag flag")
        return

    tag = f"v{version}"
    result = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)
    if tag in result.stdout:
        print(f"[release] Tag {tag} already exists, deleting...")
        subprocess.run(["git", "tag", "-d", tag], check=True)

    subprocess.run(["git", "tag", tag], check=True)
    print(f"[release] Created Git tag {tag}")

def main():
    args = parse_args()

    current_version = get_current_version()

    hotfix = args.hotfix
    patch = args.patch
    tag = args.tag
    dry = args.dry_run

    if hotfix:
        if current_version.endswith("-hotfix"):
            next_version = current_version
        else:
            next_version = f"{current_version}-hotfix"
        changelog_version = next_version
    else:
        next_version = compute_next_version(current_version, patch=patch or bool(tag), tag=tag)
        changelog_version = next_version

    print("\n======================")
    prefix = "[DRY-RUN] " if dry else "[release] "
    print(f"{prefix}Preparing Release")
    print(f"{prefix}  From: {current_version}")
    print(f"{prefix}  To:   {next_version}")
    print(f"{prefix}  Mode: {'Hotfix' if hotfix else 'Patch' if patch else 'Normal'}")
    print(f"{prefix}  Tag:  {tag or '(none)'}")
    print("======================")

    confirm = input(f"{prefix}Continue? [y/N]: ").strip().lower()
    if confirm != "y":
        print(f"{prefix}Aborted.")
        return

    update_pyproject_version(next_version, dry_run=dry)

    commits = get_commits_since_last_tag()
    added, changed, fixed, other = classify_commits(commits)

    block = format_changelog(changelog_version, added, changed, fixed, other, hotfix=hotfix)
    insert_changelog_entry(changelog_version, block, hotfix=hotfix, dry_run=dry)

    if input(f"[{'DRY-RUN' if dry else 'STAGING'}] Proceed with Git staging and tag? [y/N]: ").strip().lower() == "y":
        git_commit_and_tag(changelog_version, dry_run=dry, no_tag=args.no_tag)
    else:
        print("[release] Git tagging skipped by user.")

if __name__ == "__main__":
    main()
