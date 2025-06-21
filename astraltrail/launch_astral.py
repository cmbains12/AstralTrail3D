import argparse
import sys
import os

project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from src.engine.bootstrap import bootstrap_engine

def main():
    parser = argparse.ArgumentParser(
        description='Astral Engine Development Launcher'
    )

    parser.add_argument(
        '--mode',
        default='sandbox',
        choices=['sandbox', 'legacy'],
        help='Select mode: "sandbox" for engine testing, "legacy" to run the previous monolith version (default: sandbox)'
    )

    args = parser.parse_args()

    print(f'[LAUNCHER] Launching Astral Engine in {args.mode.upper()} mode')
    bootstrap_engine(mode=args.mode)

if __name__=='__main__':
    main()