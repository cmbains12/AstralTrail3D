import subprocess
import datetime
import sys
import re
import toml

CHANGELOG_PATH = 'CHANGELOG.md'
VERSION_FILES = ['pyproject.toml', CHANGELOG_PATH]


def get_commits_since_last_tag():
    try:
        last_tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'], encoding='utf-8'
        ).strip()
    except subprocess.CalledProcessError:
        last_tag = ''

    cmd = ['git', 'log', '--pretty=format:%B', f'{last_tag}..HEAD'] if last_tag else ['git', 'log', '--pretty=format:%B']
    output = subprocess.check_output(cmd, encoding='utf-8')
    commits = [line.strip() for line in output.split('\n') if line.strip()]
    return commits


def categorize_commits(commits):
    added, changed, fixed = [], [], []
    for msg in commits:
        lower = msg.lower()
        if lower.startswith('feat') or 'add' in lower:
            added.append(msg)
        elif lower.startswith('fix'):
            fixed.append(msg)
        elif lower.startswith('change'):
            changed.append(msg)
        else:
            changed.append(msg)
    return added, changed, fixed


def bump_version(tag: str = None):
    print(f'[RELEASE] Bumping calendar version...')
    cmd = ['bumpver', 'update']
    if tag:
        cmd += ['--tag', tag]
    subprocess.run(cmd, check=True)

def compute_next_version(current_version: str, tag: str = None):
    base = current_version.split('-')[0]
    year, build = base.split('.')
    build = int(build) + 1
    tag_suffix = f'-{tag}' if tag else ''
    return f"{year}.{build:04d}{tag_suffix}"

def get_new_version():
    with open('pyproject.toml', 'r') as f:
        data = toml.load(f)
    try:
        return data['project']['version']
    except KeyError:
        raise RuntimeError('Version not found in [project] section of pyproject.toml')


def insert_changelog_entry(version, added, changed, fixed):
    today = datetime.date.today().isoformat()
    
    entry = f'\n## [{version}] - {today} <!-- {{bumpver}} -->\n'

    if added:
        entry += '\n### Added\n' + '\n'.join(f'- {a}' for a in added)

    if changed:
        entry += '\n### Changed\n' + '\n'.join(f'- {c}' for c in changed)

    if fixed:
        entry += '\n### Fixed\n' + '\n'.join(f'- {f}' for f in fixed)

    with open(CHANGELOG_PATH, 'r+', encoding='utf-8') as f:
        content = f.read()
        content = re.sub(r'<!--\s*\{bumpver\}\s*-->', '', content)
        f.seek(0)
        f.write(entry + '\n' + content.lstrip())

    print(f'[RELEASE] Changelog updated for {version}')


def stage_changes():
    print('[RELEASE] Staging version and changelog updates...')
    subprocess.run(['git', 'add'] + VERSION_FILES, check=True)


def commit_changes(version):
    stage_changes()
    print('[RELEASE] Committing version and changelog updates...')
    subprocess.run(['git', 'commit', '-m', f'release: version {version}'], check=True)

def tag_release(version):
    print(f'[RELEASE] Tagging release version{version}...')
    subprocess.run(['git', 'tag', f'v{version}'], check=True)
    

def main():
    print('=== Astral Engine Release Script ===')

    dry_run = '--dry-run' in sys.argv
    tag = input('Optional tag (alpha, beta, rc) or leave blank: ').strip() or None

    current_version = get_new_version()
    version = compute_next_version(current_version, tag)
    print(f'\n[RELEASE] Next Version: {version}')

    commits = get_commits_since_last_tag()
    added, changed, fixed = categorize_commits(commits)
    
    if dry_run:
        print('\n[DRY-RUN] Changelog preview:')
        print(f'\n## [{version}] - {datetime.date.today().isoformat()} <!-- {{bumpver}} -->')
        if added:
            print('\n### Added\n' + '\n'.join(f'- {a}' for a in added))
        if changed:
            print('\n### Changed\n' + '\n'.join(f'- {c}' for c in changed))
        if fixed:
            print('\n### Fixed\n' + '\n'.join(f'- {f}' for f in fixed))
        print('\n[DRY-RUN] Skipping changelog write and git operations.')
        return
    
    insert_changelog_entry(version, added, changed, fixed)

    bump_version(tag)

    print('\n[RELEASE] What do you want to do with these changes?')
    print('1. Commit them immediately')
    print('2. Stage only (for later commit)')
    print('3. Do nothing')

    choice = input('Enter choice [1/2/3]: ').strip()

    if choice == '1':
        commit_changes(version)
        tag_release(version)
    elif choice == '2':
        stage_changes()
        print('[RELEASE] You can now commit manually when ready.')
    elif choice == '3':
        print('[RELEASE] No Git operations performed.')
    else:
        print('[RELEASE] Invalid choice. Exiting...')

    print(f'[RELEASE] Version {version} workflow complete.')


if __name__ == '__main__':
    main()
