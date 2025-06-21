import subprocess
import datetime
import argparse
import toml
import re
from pathlib import Path

CHANGELOG_PATH = "CHANGELOG.md"
PYPROJECT_PATH = "pyproject.toml"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    parser.add_argument("--hotfix", action="store_true", help="Apply a hotfix tag to the version")
    return parser.parse_args()

def bump_version(tag=None, dry_run=False):
    cmd = ["bumpver", "update"]
    if tag:
        cmd += ["--tag", tag]
    if dry_run:
        cmd.append("--dry")

    # capture stdout so we can parse the new version
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=True)
    match = re.search(r"New Version: ([\w\.-]+)", result.stdout)
    if not match:
        raise RuntimeError("Failed to parse new version from bumpver output")
    return match.group(1)

def get_version():
    data = toml.load(PYPROJECT_PATH)
    return data["project"]["current_version"]

def get_commits_since_last_tag():
    try:
        last_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], encoding="utf-8").strip()
    except subprocess.CalledProcessError:
        last_tag = None
    cmd = ["git", "log", "--pretty=format:%s"]
    if last_tag:
        cmd.insert(3, f"{last_tag}..HEAD")
    output = subprocess.check_output(cmd, encoding="utf-8")
    return output.strip().split("\n")

def classify_commits(commits):
    added = []
    changed = []
    fixed = []
    other = []

    for c in commits:
        c_lower = c.lower()
        if c_lower.startswith("feat:"):
            added.append(c[5:].strip())
        elif c_lower.startswith("fix:"):
            fixed.append(c[4:].strip())
        elif c_lower.startswith("change:"):
            changed.append(c[7:].strip())
        else:
            other.append(c.strip())
    return added, changed, fixed, other

def format_changelog_block(version, added, changed, fixed, other):
    today = datetime.date.today().isoformat()
    def section(title, items):
        return f"### {title}\n" + "\n".join(f"- {i}" for i in items) + "\n\n" if items else ""
    return (
        f"\n## [{version}] - {today} <!-- {{bumpver}} -->\n\n"
        + section("Added", added)
        + section("Changed", changed)
        + section("Fixed", fixed)
        + section("Other", other)
    )

def insert_changelog_entry(version, block, dry_run=False):
    changelog = Path(CHANGELOG_PATH)
    content = changelog.read_text(encoding="utf-8")
    if f"## [{version}]" in content:
        print(f"[release] Changelog already contains entry for {version}")
        return
    new_content = block + "\n" + content
    if dry_run:
        print("==== DRY RUN ====")
        print(new_content)
    else:
        changelog.write_text(new_content, encoding="utf-8")
        print(f"[release] Changelog updated with version {version}")

def main():
    args = parse_args()
    tag = "hotfix" if args.hotfix else None

    print("[release] Bumping version...")
    bump_version(tag=tag, dry_run=args.dry_run)

    version = get_version()
    print(f"[release] New version: {version}")

    print("[release] Collecting commits...")
    commits = get_commits_since_last_tag()
    added, changed, fixed, other = classify_commits(commits)

    block = format_changelog_block(version, added, changed, fixed, other)
    insert_changelog_entry(version, block, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
