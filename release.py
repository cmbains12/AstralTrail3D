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
    parser.add_argument("--hotfix", action="store_true", help="Add -hotfix to version")
    return parser.parse_args()

def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if "current_version" in line and "# {bumpver}" in line:
                return line.split("=")[1].split("#")[0].strip().strip('"')
    raise RuntimeError("current_version not found in pyproject.toml")

def compute_next_version(current_version, hotfix=False):
    year, rest = current_version.split(".")
    if "-" in rest:
        build, _ = rest.split("-")
    else:
        build = rest
    new_build = int(build) + 1
    tag = "hotfix" if hotfix else "dev"
    return f"{year}.{new_build}-{tag}"

def bump_version(new_version, dry_run=False):
    cmd = ["bumpver", "update", "--new-version", new_version]
    if dry_run:
        cmd.append("--dry")
    subprocess.run(cmd, check=True)
    return new_version

def get_commits_since_last_tag():
    try:
        last_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], encoding="utf-8").strip()
        range_spec = f"{last_tag}..HEAD"
    except subprocess.CalledProcessError:
        range_spec = "HEAD"
    commits = subprocess.check_output(["git", "log", range_spec, "--pretty=format:%s"], encoding="utf-8")
    return commits.strip().split("\n")

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
        f"\n## [{version}] - {today} <!-- {{bumpver}} -->\n\n"
        + sec("Added", added)
        + sec("Changed", changed)
        + sec("Fixed", fixed)
        + sec("Other", other)
    )

def insert_changelog_entry(version, block, dry_run=False):
    changelog = Path(CHANGELOG_PATH)
    content = changelog.read_text(encoding="utf-8")

    # Robust version check
    pattern = rf'^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}} <!-- {{bumpver}} -->'
    if re.search(pattern, content, re.MULTILINE):
        print(f"[release] Changelog already contains version {version}")
        return

    new_content = block + content
    if dry_run:
        print("==== DRY RUN ====\n")
        print(new_content)
    else:
        changelog.write_text(new_content, encoding="utf-8")
        print(f"[release] Changelog updated with version {version}")

def main():
    args = parse_args()

    current = get_current_version()
    next_version = compute_next_version(current, args.hotfix)

    print(f"[release] Bumping from {current} → {next_version}")
    bump_version(next_version, dry_run=args.dry_run)

    commits = get_commits_since_last_tag()
    added, changed, fixed, other = classify_commits(commits)

    block = format_changelog(next_version, added, changed, fixed, other)
    insert_changelog_entry(next_version, block, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
