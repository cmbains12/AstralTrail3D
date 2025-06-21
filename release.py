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
    parser.add_argument("--hotfix", action="store_true", help="Append to current version as hotfix")
    parser.add_argument("--patch", action="store_true", help="Bump version without changing tag")
    parser.add_argument("--tag", type=str, help="Suffix tag to apply (e.g., dev, alpha)")
    parser.add_argument("--no-tag", action="store_true", help="Skip creating git tag")
    return parser.parse_args()

def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):
                return line.split("=")[1].split("#")[0].strip().strip('"')
    raise RuntimeError("version not found in pyproject.toml")

def compute_next_version(current_version, patch=False, tag=None):
    year, rest = current_version.split(".")
    build = rest.split("-")[0]
    new_build = int(build) + 1 if not patch else int(build)
    suffix = tag if tag else rest.split("-")[1] if "-" in rest else "dev"
    return f"{year}.{new_build}-{suffix}"

def update_file(path, pattern, replacement, dry_run=False):
    content = Path(path).read_text(encoding="utf-8")
    new_content = re.sub(pattern, replacement, content)
    if dry_run:
        print(f"[dry-run] Would update {path}:")
        print("---\n" + new_content + "\n---")
    else:
        Path(path).write_text(new_content, encoding="utf-8")

def update_pyproject_version(new_version, dry_run=False):
    pattern = r'version\s*=\s*"[\d\.]+-[\w]+"'
    replacement = f'version = "{new_version}"'
    update_file(PYPROJECT_PATH, pattern, replacement, dry_run)
    if not dry_run:
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

def format_changelog(version, added, changed, fixed, other, hotfix=False):
    today = datetime.date.today().isoformat()
    def sec(title, lines): return f"### {title}\n" + "\n".join(f"- {l}" for l in lines) + "\n\n" if lines else ""
    if hotfix:
        return (
            f"\n## [{version}] - {today}\n\n"
            f"#### Hotfix patch ({today})\n"
            + sec("Added", added)
            + sec("Changed", changed)
            + sec("Fixed", fixed)
            + sec("Other", other)
        )
    else:
        return (
            f"\n## [{version}] - {today}\n\n"
            + sec("Added", added)
            + sec("Changed", changed)
            + sec("Fixed", fixed)
            + sec("Other", other)
        )

def insert_changelog_entry(version, block, dry_run=False, hotfix=False):
    changelog = Path(CHANGELOG_PATH)
    content = changelog.read_text(encoding="utf-8")
    if hotfix and f"[{version}]" in content:
        if dry_run:
            print(f"[DRY-RUN] Would append hotfix block to existing version {version}")
        else:
            updated = re.sub(f"(## \\[{version}\\].*?)(?=\n## |\Z)", r"\1" + block, content, flags=re.DOTALL)
            changelog.write_text(updated, encoding="utf-8")
            print(f"[release] Appended hotfix changes to version {version}")
        return

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

    subprocess.run(["git", "add", "pyproject.toml", "CHANGELOG.md"], check=True)
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("[release] Nothing to commit.")
        return

    subprocess.run(["git", "commit", "-m", f"release: v{version}"], check=True)

    if not no_tag:
        tag = f"v{version}"
        existing = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)
        if tag in existing.stdout:
            subprocess.run(["git", "tag", "-d", tag], check=True)
        subprocess.run(["git", "tag", tag], check=True)
        print(f"[release] Created tag {tag}")

def main():
    args = parse_args()
    current = get_current_version()

    is_hotfix = args.hotfix
    is_patch = args.patch

    tag = args.tag or input("[release] Enter tag (e.g., dev, alpha, beta): ").strip()
    if not tag:
        tag = "dev"

    if is_hotfix:
        next_version = current  # no bump
    else:
        next_version = compute_next_version(current, patch=is_patch, tag=tag)

    label = "DRY-RUN" if args.dry_run else "release"
    print("="*22)
    print(f"[{label}] Preparing Release")
    print(f"[{label}]   From: {current}")
    print(f"[{label}]   To:   {next_version}")
    print(f"[{label}]   Mode: {'Hotfix' if is_hotfix else 'Patch' if is_patch else 'Normal'}")
    print(f"[{label}]   Tag:  {tag}")
    print("="*22)

    confirm = input(f"[{label}] Continue? [y/N]: ").strip().lower()
    if confirm != "y":
        print(f"[{label}] Aborted.")
        return

    update_pyproject_version(next_version, dry_run=args.dry_run)

    commits = get_commits_since_last_tag()
    added, changed, fixed, other = classify_commits(commits)

    block = format_changelog(next_version if not is_hotfix else f"{next_version}-hotfix", added, changed, fixed, other, hotfix=is_hotfix)
    insert_changelog_entry(next_version if not is_hotfix else f"{next_version}-hotfix", block, dry_run=args.dry_run, hotfix=is_hotfix)

    stage = input("[STAGING] Proceed with commit and tag? [y/N]: ").strip().lower()
    if stage == "y":
        git_commit_and_tag(next_version if not is_hotfix else f"{next_version}-hotfix", dry_run=args.dry_run, no_tag=args.no_tag)
    else:
        print("[release] Commit skipped.")

if __name__ == "__main__":
    main()
