# release.py

import subprocess
import datetime

CHANGELOG_PATH = "CHANGELOG.md"

def insert_changelog_entry(version):
    today = datetime.date.today().isoformat()
    commits = get_commits_since_last_tag()

    added = []
    changed = []
    fixed = []

    for c in commits:
        c_lower = c.lower()
        if c_lower.startswith("feat:"):
            added.append(c[5:].strip())
        elif c_lower.startswith("fix:"):
            fixed.append(c[4:].strip())
        elif c_lower.startswith("change:"):
            changed.append(c[7:].strip())
        else:
            changed.append(c.strip())  # fallback category

    def format_section(title, items):
        if not items:
            return f"### {title}\n- \n"
        return f"### {title}\n" + "\n".join(f"- {item}" for item in items) + "\n"

    entry = (
        f"\n## [{version}] - {today} <!-- {{bumpver}} -->\n\n"
        + format_section("Added", added)
        + "\n"
        + format_section("Changed", changed)
        + "\n"
        + format_section("Fixed", fixed)
    )

    with open(CHANGELOG_PATH, "r+", encoding="utf-8") as f:
        content = f.read()
        if f"## [{version}]" in content:
            print(f"[release] Entry for version {version} already exists.")
            return
        f.seek(0)
        f.write(entry + "\n" + content)


def get_commits_since_last_tag():
    try:
        last_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            encoding="utf-8"
        ).strip()
    except subprocess.CalledProcessError:
        last_tag = None

    if last_tag:
        cmd = ["git", "log", f"{last_tag}..HEAD", "--pretty=format:%s"]
    else:
        cmd = ["git", "log", "--pretty=format:%s"]

    output = subprocess.check_output(cmd, encoding="utf-8")
    commits = output.strip().split("\n")
    return commits


def bump_version(tag=None):
    cmd = ["bumpver", "update"]
    if tag:
        cmd += ["--tag", tag]
    subprocess.run(cmd, check=True)

def insert_changelog_entry(version):
    today = datetime.date.today().isoformat()
    entry = f"\n## [{version}] - {today} <!-- {{bumpver}} -->\n\n### Added\n- \n\n### Changed\n- \n\n### Fixed\n- \n"

    with open(CHANGELOG_PATH, "r+", encoding="utf-8") as f:
        content = f.read()
        if f"## [{version}]" in content:
            print(f"[release] Entry for version {version} already exists.")
            return
        f.seek(0)
        f.write(entry + content)

def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("current_version"):
                version = line.split("=")[1].split("#")[0].strip().strip('"')
                return version
    raise RuntimeError("Version not found in pyproject.toml")

def main():
    bump_version()
    version = get_version()
    insert_changelog_entry(version)

    print(f"[release] Commits since last tag:")
    for c in get_commits_since_last_tag():
        print(f" - {c}")

if __name__ == "__main__":
    main()
