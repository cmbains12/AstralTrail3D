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
    parser.add_argument("--hotfix", action="store_true", help="Append hotfix entry without version bump")
    parser.add_argument("--patch", action="store_true", help="Increment version without changing tag")
    parser.add_argument("--tag", type=str, help="Tag to append to version string (e.g. dev, beta)")
    parser.add_argument("--no-tag", action="store_true", help="Disable Git tagging")
    return parser.parse_args()

def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"')
    raise RuntimeError("Version not found in pyproject.toml")

def compute_next_version(version: str, patch: bool, tag: str):
    year, rest = version.split(".")
    build = rest.split("-")[0]
    new_build = int(build) + (1 if patch else 0)
    base_version = f"{year}.{new_build}"
    return f"{base_version}-{tag}" if tag else base_version

def get_last_version_from_changelog():
    with open(CHANGELOG_PATH, encoding="utf-8") as f:
        for line in f:
            match = re.match(r'^## \[(.*?)\] - \d{4}-\d{2}-\d{2}', line)
            if match:
                return match.group(1)
    return None

def get_commits_since_tag(version):
    tag = f"v{version}"
    try:
        subprocess.check_output(["git", "rev-parse", "--verify", tag], stderr=subprocess.DEVNULL)
        range_spec = f"{tag}..HEAD"
    except subprocess.CalledProcessError:
        return []
    commits = subprocess.check_output(["git", "log", range_spec, "--pretty=format:%s"], encoding="utf-8")
    return commits.strip().split("\n") if commits.strip() else []

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

def format_changelog(version, added, changed, fixed, other, hotfix=False):
    today = datetime.date.today().isoformat()
    def sec(title, lines): return f"### {title}\n" + "\n".join(f"- {l}" for l in lines) + "\n\n" if lines else ""
    header = f"\n## [{version}] - {today}\n\n"
    if hotfix:
        header += f"#### Hotfix patch ({today})\n"
    return header + sec("Added", added) + sec("Changed", changed) + sec("Fixed", fixed) + sec("Other", other)

def update_pyproject_version(new_version, dry_run=False):
    content = Path(PYPROJECT_PATH).read_text(encoding="utf-8")
    new_content = re.sub(r'version\s*=\s*"[^"]+"', f'version = "{new_version}"', content)
    if dry_run:
        print(f"[DRY-RUN] Would update pyproject.toml to version: {new_version}")
    else:
        Path(PYPROJECT_PATH).write_text(new_content, encoding="utf-8")
        print(f"[release] pyproject.toml updated to version {new_version}")

def insert_changelog_entry(version, block, dry_run=False):
    changelog = Path(CHANGELOG_PATH)
    content = changelog.read_text(encoding="utf-8")
    if f"## [{version}]" in content:
        print(f"[release] Changelog already contains version {version}")
        return
    new_content = block + content
    if dry_run:
        print(f"[DRY-RUN] Would insert changelog entry:\n{block}")
    else:
        changelog.write_text(new_content, encoding="utf-8")
        print(f"[release] Changelog updated with version {version}")

def git_commit_and_tag(version, dry_run=False, no_tag=False):
    if dry_run:
        print(f"[DRY-RUN] Would commit and tag version {version}")
        return

    subprocess.run(["git", "add", "pyproject.toml", "CHANGELOG.md"], check=True)
    subprocess.run(["git", "commit", "-m", f"release: v{version}"], check=True)

    if no_tag:
        print("[release] Skipping Git tag creation due to --no-tag flag.")
        return

    tag = f"v{version}"
    result = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)

    if tag in result.stdout:
        response = input(f"[release] Tag '{tag}' already exists. Overwrite? [y/N]: ").strip().lower()
        if response != 'y':
            print("[release] Skipping tag creation.")
            return
        subprocess.run(["git", "tag", "-d", tag], check=True)

    subprocess.run(["git", "tag", tag], check=True)
    print(f"[release] Created Git tag {tag}")

def main():
    args = parse_args()
    dry = args.dry_run
    patch = args.patch
    hotfix = args.hotfix
    tag = args.tag or input("[release] Tag (e.g. dev, beta): ").strip()

    current_version = get_current_version()

    if hotfix:
        if current_version.endswith("-hotfix"):
            version = current_version
        else:
            version = f"{current_version}-hotfix"
    else:
        version = compute_next_version(current_version, patch=patch or not hotfix, tag=tag)

    print("\n======================")
    label = "[DRY-RUN]" if dry else "[release]"
    print(f"{label} Preparing Release")
    print(f"{label}   From: {current_version}")
    print(f"{label}   To:   {version}")
    print(f"{label}   Mode: {'Hotfix' if hotfix else 'Patch' if patch else 'Normal'}")
    print(f"{label}   Tag:  {tag}")
    print("======================")
    if input(f"{label} Continue? [y/N]: ").strip().lower() != 'y':
        print(f"{label} Aborted.")
        return

    update_pyproject_version(version, dry_run=dry)

    commits = get_commits_since_tag(get_last_version_from_changelog())
    if not commits:
        print(f"{label} No new commits found. Nothing to do.")
        return

    added, changed, fixed, other = classify_commits(commits)
    block = format_changelog(version, added, changed, fixed, other, hotfix=hotfix)
    insert_changelog_entry(version, block, dry_run=dry)

    if input("[release] Proceed with Git staging and tag? [y/N]: ").strip().lower() == 'y':
        git_commit_and_tag(version, dry_run=dry, no_tag=args.no_tag)

if __name__ == "__main__":
    main()
