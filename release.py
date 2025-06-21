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
    parser.add_argument("--hotfix", action="store_true", help="Apply hotfix without incrementing version")
    parser.add_argument("--patch", action="store_true", help="Force version increment for patch")
    parser.add_argument("--tag", type=str, help="Optional version tag (e.g., dev, beta)")
    parser.add_argument("--no-tag", action="store_true", help="Skip git tag")
    return parser.parse_args()

def get_current_version():
    with open(PYPROJECT_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):
                return line.split("=")[1].split("#")[0].strip().strip('"')
    raise RuntimeError("version not found in pyproject.toml")

def compute_next_version(current_version, patch=False, hotfix=False, cli_tag=None):
    base_version, *existing_tags = current_version.split("-")
    year, build = base_version.split(".")

    if hotfix:
        return current_version  # do not increment

    new_build = int(build) + 1 if patch or not hotfix else int(build)
    tag = cli_tag or input("Enter version tag (e.g., dev, beta): ").strip()
    return f"{year}.{new_build}-{tag}"

def update_pyproject_version(new_version, dry_run=False):
    content = Path(PYPROJECT_PATH).read_text(encoding="utf-8")
    new_content = re.sub(r'version\s*=\s*"[\d\.]+(?:-[\w]+)?"', f'version = "{new_version}"', content)
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

def format_changelog_section(title, lines):
    return f"### {title}\n" + "\n".join(f"- {l}" for l in lines) + "\n\n" if lines else ""

def insert_changelog_entry(version, block, dry_run=False, hotfix=False):
    changelog = Path(CHANGELOG_PATH)
    content = changelog.read_text(encoding="utf-8")

    if f"## [{version}]" in content:
        if hotfix:
            # Insert hotfix changes inside the existing version block
            pattern = rf'(## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}\n\n)'
            insertion = f"#### Hotfix changes ({datetime.date.today().isoformat()})\n\n" + block
            new_content = re.sub(pattern, rf"\1{insertion}", content)
            if dry_run:
                print(f"[DRY-RUN] Would insert hotfix changes into changelog for version {version}")
            else:
                changelog.write_text(new_content, encoding="utf-8")
                print(f"[release] Appended hotfix changes to version {version}")
        else:
            print(f"[release] Changelog already contains version {version}")
        return

    new_content = block + content
    if dry_run:
        print(f"[DRY-RUN] Would insert new changelog block:\n---\n{block}\n---")
    else:
        changelog.write_text(new_content, encoding="utf-8")
        print(f"[release] Changelog updated with version {version}")

def git_commit_and_tag(version, dry_run=False, no_tag=False):
    if dry_run:
        print(f"[DRY-RUN] Would commit and tag version {version}")
        return

    proceed = input("[STAGING] Proceed with commit and tag? [y/N]: ").strip().lower()
    if proceed != "y":
        print("[STAGING] Aborted before commit/tag.")
        return

    subprocess.run(["git", "add", PYPROJECT_PATH, CHANGELOG_PATH], check=True)
    subprocess.run(["git", "commit", "-m", f"release: v{version}"], check=True)

    if no_tag:
        print(f"[release] Skipping git tag for v{version}")
        return

    tag = f"v{version}"
    result = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)
    if tag in result.stdout:
        print(f"[release] Tag {tag} already exists, deleting...")
        subprocess.run(["git", "tag", "-d", tag], check=True)

    subprocess.run(["git", "tag", tag], check=True)
    print(f"[release] Created tag {tag}")

def main():
    args = parse_args()
    current = get_current_version()
    next_version = compute_next_version(current, patch=args.patch, hotfix=args.hotfix, cli_tag=args.tag)

    mode = "Hotfix" if args.hotfix else ("Patch" if args.patch else "Normal")
    print("======================")
    label = "[DRY-RUN]" if args.dry_run else "[release]"
    print(f"{label} Preparing Release")
    print(f"{label}   From: {current}")
    print(f"{label}   To:   {next_version}")
    print(f"{label}   Mode: {mode}")
    print(f"{label}   Tag:  {args.tag or '(prompted)'}")
    print("======================")
    confirm = input(f"{label} Continue? [y/N]: ").strip().lower()
    if confirm != "y":
        print(f"{label} Aborted.")
        return

    update_pyproject_version(next_version, dry_run=args.dry_run)
    commits = get_commits_since_last_tag()
    added, changed, fixed, other = classify_commits(commits)

    changelog_block = (
        format_changelog_section("Added", added) +
        format_changelog_section("Changed", changed) +
        format_changelog_section("Fixed", fixed) +
        format_changelog_section("Other", other)
    )

    formatted_block = f"\n## [{next_version}] - {datetime.date.today().isoformat()}\n\n" + changelog_block
    insert_changelog_entry(next_version, changelog_block, dry_run=args.dry_run, hotfix=args.hotfix)
    git_commit_and_tag(next_version, dry_run=args.dry_run, no_tag=args.no_tag)

if __name__ == "__main__":
    main()
