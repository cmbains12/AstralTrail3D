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
    parser.add_argument("--hotfix", action="store_true", help="Mark as hotfix (no version bump, appends to last block)")
    parser.add_argument("--patch", action="store_true", help="Increment version as a patch")
    parser.add_argument("--tag", type=str, help="Optional version tag (e.g., dev, beta, stable)")
    parser.add_argument("--no-tag", action="store_true", help="Skip Git tag creation")
    return parser.parse_args()

def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"')
    raise RuntimeError("version not found in pyproject.toml")

def compute_next_version(current_version, patch=False, hotfix=False, tag=None):
    base, *existing_tags = current_version.split("-")
    tags = set(existing_tags)

    if hotfix:
        tags.add("hotfix")
    if tag:
        tags.add(tag)

    if patch and not hotfix:
        year, build = base.split(".")
        base = f"{year}.{int(build)+1}"

    tag_suffix = "-" + "-".join(sorted(tags)) if tags else ""
    return base + tag_suffix

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

def format_changelog_block(version, added, changed, fixed, other, hotfix=False):
    today = datetime.date.today().isoformat()
    def sec(title, lines): return f"### {title}\n" + "\n".join(f"- {l}" for l in lines) + "\n\n" if lines else ""

    if hotfix:
        return f"\n#### Hotfix patch ({today})\n\n" + sec("Added", added) + sec("Changed", changed) + sec("Fixed", fixed) + sec("Other", other)
    else:
        return f"\n## [{version}] - {today}\n\n" + sec("Added", added) + sec("Changed", changed) + sec("Fixed", fixed) + sec("Other", other)

def update_pyproject_version(version, dry_run=False):
    content = Path(PYPROJECT_PATH).read_text(encoding="utf-8")
    new_content = re.sub(r'version\s*=\s*"[^"]+"', f'version = "{version}"', content)
    if dry_run:
        print(f"[DRY-RUN] Would update pyproject.toml to version: {version}")
    else:
        Path(PYPROJECT_PATH).write_text(new_content, encoding="utf-8")
        print(f"[release] pyproject.toml updated to version {version}")

def insert_changelog_entry(version, block, hotfix=False, dry_run=False):
    changelog = Path(CHANGELOG_PATH)
    content = changelog.read_text(encoding="utf-8")

    if hotfix:
        pattern = rf"(## \[{re.escape(version)}\].*?)(?=\n## |\Z)"
        updated = re.sub(pattern, r"\1" + block, content, flags=re.DOTALL)
        if updated == content:
            raise RuntimeError(f"Could not find changelog block for version {version}")
        if dry_run:
            print(f"[DRY-RUN] Would insert hotfix changes into changelog for version {version}")
        else:
            changelog.write_text(updated, encoding="utf-8")
            print(f"[release] Appended hotfix changes to version {version}")
    else:
        if f"## [{version}]" in content:
            print(f"[release] Changelog already contains version {version}")
            return
        new_content = block + content
        if dry_run:
            print(f"[DRY-RUN] Would add new changelog block:\n---\n{block}\n---")
        else:
            changelog.write_text(new_content, encoding="utf-8")
            print(f"[release] Changelog updated with version {version}")

def git_commit_and_tag(version, dry_run=False, no_tag=False):
    if dry_run:
        print(f"[DRY-RUN] Would commit and tag version {version}")
        return

    subprocess.run(["git", "add", PYPROJECT_PATH, CHANGELOG_PATH], check=True)
    subprocess.run(["git", "commit", "-m", f"release: v{version}"], check=True)

    if no_tag:
        return

    tag = f"v{version}"
    existing = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)
    if tag in existing.stdout:
        print(f"[release] Tag {tag} already exists, deleting...")
        subprocess.run(["git", "tag", "-d", tag], check=True)

    subprocess.run(["git", "tag", tag], check=True)
    print(f"[release] Created tag {tag}")

def main():
    args = parse_args()
    dry = args.dry_run
    hotfix = args.hotfix
    patch = args.patch
    tag = args.tag

    current = get_current_version()
    next_version = compute_next_version(current, patch=patch, hotfix=hotfix, tag=tag)

    mode = "Hotfix" if hotfix else "Patch" if patch else "Normal"
    print("\n======================")
    print(f"[{'DRY-RUN' if dry else 'release'}] Preparing Release")
    print(f"[{'DRY-RUN' if dry else 'release'}]   From: {current}")
    print(f"[{'DRY-RUN' if dry else 'release'}]   To:   {next_version}")
    print(f"[{'DRY-RUN' if dry else 'release'}]   Mode: {mode}")
    print(f"[{'DRY-RUN' if dry else 'release'}]   Tag:  {tag or '(none)'}")
    print("======================")
    proceed = input(f"[{'DRY-RUN' if dry else 'release'}] Continue? [y/N]: ")
    if proceed.strip().lower() != "y":
        print(f"[{'DRY-RUN' if dry else 'release'}] Aborted.")
        return

    update_pyproject_version(next_version, dry_run=dry)
    commits = get_commits_since_last_tag()
    added, changed, fixed, other = classify_commits(commits)

    block = format_changelog_block(next_version, added, changed, fixed, other, hotfix=hotfix)
    insert_changelog_entry(next_version, block, hotfix=hotfix, dry_run=dry)

    stage = input(f"[{'DRY-RUN' if dry else 'STAGING'}] Proceed with commit and tag? [y/N]: ")
    if stage.strip().lower() == "y":
        git_commit_and_tag(next_version, dry_run=dry, no_tag=args.no_tag)
    else:
        print(f"[{'DRY-RUN' if dry else 'release'}] Commit and tag skipped.")

if __name__ == "__main__":
    main()
