import subprocess
import datetime
import sys
import re
import toml
import argparse

CHANGELOG_PATH = 'CHANGELOG.md'
VERSION_FILES = ['pyproject.toml', CHANGELOG_PATH]

parser = argparse.ArgumentParser()
parser.add_argument('--tag', type=str, help='Optional version tag (e.g., alpha, beta)')
parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
parser.add_argument('--force-insert', action='store_true', help='Force changelog entry insertion even if entry exists')
args = parser.parse_args()

tag = args.tag
dry_run = args.dry_run

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
        try:
            return data['tool']['poetry']['version']
        except KeyError:
            raise RuntimeError('Version not found in pyproject.toml')


def insert_changelog_entry(version, added, changed, fixed):
    today = datetime.date.today().isoformat()
    
    # Prevent duplicate version entries
    with open(CHANGELOG_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        if f'## [{version}]' in content and not args.force_insert:
            print(f'[RELEASE] Changelog already contains version {version}. Use --force-insert to override.')
            return
        
    
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
    try:
        subprocess.run(['git', 'tag', f'v{version}'], check=True)
    except subprocess.CalledProcessError:
        print(f'[WARNING] Tag v{version} already exists. Skipping tag creation.')

def git_tag_exists(version):
    tags = subprocess.check_output(['git', 'tag'], encoding='utf-8').splitlines()
    return f'v{version}' in tags

def main():
    print('=== Astral Engine Release Script ===')
    
    def git_is_clean():
        result = subprocess.run(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
        return result.stdout.strip() == ''

    if not git_is_clean():
        print("[ERROR] Git working directory is not clean. Commit or stash changes before releasing.")
        sys.exit(1)

    current_version = get_new_version()
    next_version = compute_next_version(current_version, tag)
    print(f'\n[RELEASE] Next Version: {next_version}')

    commits = get_commits_since_last_tag()
    added, changed, fixed = categorize_commits(commits)

    if dry_run:
        print('\n[DRY-RUN] Changelog preview:')
        print(f'\n## [{next_version}] - {datetime.date.today().isoformat()} <!-- {{bumpver}} -->')
        if added:
            print('\n### Added\n' + '\n'.join(f'- {a}' for a in added))
        if changed:
            print('\n### Changed\n' + '\n'.join(f'- {c}' for c in changed))
        if fixed:
            print('\n### Fixed\n' + '\n'.join(f'- {f}' for f in fixed))
        print('\n[DRY-RUN] Skipping changelog write and git operations.')
        return
    confirm = input(f'[RELEASE] Bump version to {next_version}? [y/N]: ').strip().lower()
    if confirm not in ('y', 'yes'):
        print('[RELEASE] Version bump cancelled by user.')
        sys.exit(0)    
    bump_version(tag)
    final_version = get_new_version()

    insert_changelog_entry(final_version, added, changed, fixed)
    subprocess.run(['git', '--no-pager', 'diff', '--staged'])

    print('\n[RELEASE] What do you want to do with these changes?')
    print('1. Commit them immediately')
    print('2. Stage only (for later commit)')
    print('3. Do nothing')

    choice = input('Enter choice [1/2/3]: ').strip()

    if git_tag_exists(final_version):
        print(f"[ERROR] Version {final_version} is already tagged.")
        sys.exit(1)


    if choice == '1':
        commit_changes(final_version)
        tag_release(final_version)
    elif choice == '2':
        stage_changes()
        print('[RELEASE] You can now commit manually when ready.')
    elif choice == '3':
        print('[RELEASE] No Git operations performed.')
    else:
        print('[RELEASE] Invalid choice. Exiting...')

    print(f'[RELEASE] Version {final_version} workflow complete.')


if __name__ == '__main__':
    main()
