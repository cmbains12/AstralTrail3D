import subprocess
import datetime
import argparse
import re
from pathlib import Path

CHANGELOG_PATH = "CHANGELOG.md"
PYPROJECT_PATH = "pyproject.toml"
BUMPVER_PATH = ".bumpver.toml"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--hotfix", action="store_true", help="Add -hotfix to version")
    return parser.parse_args()

def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):

                return line.split("=")[1].split("#")[0].strip().strip('"')
    raise RuntimeError("version not found in pyproject.toml")

def compute_next_version(current_version, hotfix=False):
    year, rest = current_version.split(".")
    build = rest.split("-")[0]
    new_build = int(build) + 1
    tag = "hotfix" if hotfix else "dev"
    return f"{year}.{new_build}-{tag}"

def update_file(path, pattern, replacement, dry_run=False):
    content = Path(path).read_text(encoding="utf-8")
    new_content = re.sub(pattern, replacement, content)
    if dry_run:
        print(f"[dry-run] Would update {path}:\n---\n{new_content}\n---")
    else:
        Path(path).write_text(new_content, encoding="utf-8")

def bump_version(new_version, dry_run=False):
    update_pyproject_version(new_version, dry_run)
    return new_version

def get_last_version_from_changelog():
    with open(CHANGELOG_PATH, encoding="utf-8") as f:
        for line in f:
            match = re.match(r'^## \[(\d{4}\.\d+)(?:-[\w]+)?\] - \d{4}-\d{2}-\d{2}', line)
            if match:
                return match.group(1)
    return None  # No previous version found

def get_commits_since_last_tag():
    try:
        last_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], encoding="utf-8").strip()
        if last_tag:
            range_spec = f"{last_tag}..HEAD"
        else:
            raise subprocess.CalledProcessError(1, "git describe")
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
        print(f"[dry-run] Would insert changelog entry:\n---\n{block}\n---")
    else:
        changelog.write_text(new_content, encoding="utf-8")
        print(f"[release] Changelog updated with version {version}")

def update_pyproject_version(new_version, dry_run=False):
    content = Path(PYPROJECT_PATH).read_text(encoding="utf-8")
    new_content = re.sub(
        r'version\s*=\s*"[\d\.]+-[\w]+"',
        f'version = "{new_version}"',
        content
    )

    if dry_run:
        print("==== DRY RUN ====\n")
        print("[release] Would update pyproject.toml version to:", new_version)
    else:
        Path(PYPROJECT_PATH).write_text(new_content, encoding="utf-8")
        print(f"[release] pyproject.toml updated to version {new_version}")

def git_commit_and_tag(version, dry_run=False):
    if dry_run:
        print(f"[dry-run] Would commit and tag version {version}")
        return

    subprocess.run(["git", "add", "pyproject.toml", "CHANGELOG.md"], check=True)
    subprocess.run(["git", "commit", "-m", f"release: v{version}"], check=True)

    tag = f"v{version}"

    result = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)
    if tag in result.stdout:
        print(f"[release] Tag {tag} already exists, deleting...")
        subprocess.run(["git", "tag", "-d", tag], check=True)

    subprocess.run(["git", "tag", tag], check=True)
    print(f"[release] Created commit and tag {tag}")

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
    git_commit_and_tag(next_version, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
