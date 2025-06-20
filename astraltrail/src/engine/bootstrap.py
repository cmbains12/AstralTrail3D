import sys
import os
import importlib

def bootstrap_engine(mode='game'):
    print(f'[BOOTSTRAP] Launching Astral Engine in {mode.upper()} mode.')

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    if root not in sys.path:
        sys.path.insert(0, root)

    if mode=='legacy':
        print('[BOOTSTRAP] Running legacy monolith prototype...')

        legacy = importlib.import_module('legacy.legacy_monolith')
        legacy.main()
        return
    
    if mode == 'sandbox':
        print('[BOOTSTRAP] Running sandbox demo...')
        from demo import sandbox
        sandbox.main()
        return

    else:
        print(f'[BOOTSTRAP] Unknown mode: {mode}')
        sys.exit(1)


if __name__=='__main__': 
    bootstrap_engine('sandbox')