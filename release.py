import subprocess
import datetime
import argparse
import re
from pathlib import Path

CHANGELOG_PATH = "CHANGELOG.md"
PYPROJECT_PATH = "pyproject.toml"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--hotfix", action="store_true", help="Create a hotfix without changing version")
    parser.add_argument("--patch", action="store_true", help="Patch: increment build number only")
    parser.add_argument("--tag", type=str, help="Optional tag suffix (e.g. dev, test, rc)")
    parser.add_argument("--no-tag", action="store_true", help="Skip Git tagging")
    return parser.parse_args()

def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"')
    raise RuntimeError("version not found in pyproject.toml")

def compute_next_version(current_version, patch=False, tag=None):
    year, rest = current_version.split(".")
    build_part = rest.split("-")[0]
    new_build = int(build_part) + (1 if patch else 0)
    suffix = tag or rest.split("-")[1] if "-" in rest else ""
    return f"{year}.{new_build}-{suffix}" if suffix else f"{year}.{new_build}"

def update_pyproject_version(version, dry_run=False):
    content = Path(PYPROJECT_PATH).read_text()
    new_content = re.sub(r'version\s*=\s*"[^"]+"', f'version = "{version}"', content)
    if dry_run:
        print(f"[DRY-RUN] Would update pyproject.toml to version: {version}")
    else:
        Path(PYPROJECT_PATH).write_text(new_content)
        print(f"[release] pyproject.toml updated to version {version}")

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

def format_changelog_block(version, added, changed, fixed, other, hotfix=False):
    today = datetime.date.today().isoformat()
    header = f"\n## [{version}] - {today}\n\n"
    if hotfix:
        header += f"#### Hotfix patch ({today})\n"
    def sec(title, items): return f"### {title}\n" + "\n".join(f"- {i}" for i in items) + "\n\n" if items else ""
    return header + sec("Added", added) + sec("Changed", changed) + sec("Fixed", fixed) + sec("Other", other)

def insert_changelog_entry(version, block, dry_run=False):
    content = Path(CHANGELOG_PATH).read_text()
    if f"## [{version}]" in content:
        raise RuntimeError(f"Changelog already has version {version}")
    new_content = block + content
    if dry_run:
        print(f"[DRY-RUN] Would update changelog with block:\n{block}")
    else:
        Path(CHANGELOG_PATH).write_text(new_content)
        print(f"[release] Changelog updated with version {version}")

def git_commit_and_tag(version, dry_run=False, no_tag=False):
    if dry_run:
        print(f"[DRY-RUN] Would stage, commit, and tag {version}")
        return
    subprocess.run(["git", "add", PYPROJECT_PATH, CHANGELOG_PATH], check=True)
    subprocess.run(["git", "commit", "-m", f"release: v{version}"], check=True)
    if no_tag:
        return
    tag = f"v{version}"
    result = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)
    if tag in result.stdout:
        subprocess.run(["git", "tag", "-d", tag], check=True)
    subprocess.run(["git", "tag", tag], check=True)
    print(f"[release] Created Git tag {tag}")

def prompt_confirm(message, dry_run=False):
    prefix = "[DRY-RUN] " if dry_run else "[release] "
    response = input(f"{prefix}{message} [y/N]: ").strip().lower()
    return response == "y"

def main():
    args = parse_args()
    dry = args.dry_run
    hotfix = args.hotfix
    patch = args.patch
    tag = args.tag
    no_tag = args.no_tag

    current_version = get_current_version()

    if hotfix:
        if current_version.endswith("-hotfix"):
            next_version = current_version
        else:
            next_version = f"{current_version}-hotfix"

        changelog_version = next_version
    else:
        next_version = compute_next_version(current_version, patch=patch, tag=tag)
        changelog_version = next_version

    print("======================")
    print(f"{'[DRY-RUN]' if dry else '[release]'} Preparing Release")
    print(f"{'[DRY-RUN]' if dry else '[release]'}   From: {current_version}")
    print(f"{'[DRY-RUN]' if dry else '[release]'}   To:   {changelog_version}")
    print(f"{'[DRY-RUN]' if dry else '[release]'}   Mode: {'Hotfix' if hotfix else 'Patch' if patch else 'Normal'}")
    print(f"{'[DRY-RUN]' if dry else '[release]'}   Tag:  {tag or '(none)'}")
    print("======================")
    if not prompt_confirm("Continue?", dry):
        print("[release] Aborted.")
        return

    update_pyproject_version(next_version, dry_run=dry)

    commits = get_commits_since_last_tag()
    added, changed, fixed, other = classify_commits(commits)
    changelog_block = format_changelog_block(changelog_version, added, changed, fixed, other, hotfix=hotfix)

    insert_changelog_entry(changelog_version, changelog_block, dry_run=dry)

    if prompt_confirm("Proceed with Git staging and tag?", dry):
        git_commit_and_tag(changelog_version, dry_run=dry, no_tag=no_tag)

if __name__ == "__main__":
    main()
