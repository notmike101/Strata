"""Check experimental accepted-usage routing guards without loading a model.

Usage: python tools/test_accepted_usage_modes.py ENGINE [--library-dir DIRECTORY]
"""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('engine', type=Path)
    parser.add_argument('--library-dir', action='append', default=[])
    args = parser.parse_args()
    env = {k: v for k, v in os.environ.items() if not k.startswith('STRATA_')}
    env['PATH'] = os.pathsep.join(args.library_dir + [env.get('PATH', '')])
    env['STRATA_SERIAL_ADAPT_TOKENS'] = '0'
    env['STRATA_SERIAL_ADAPT_MIN_PROMPT'] = '0'
    cases = [
        ('1', ['--spec-split'], True),
        ('1', ['--spec-split', '--no-spec-split'], False),
        ('0', ['--spec-split'], False),
        ('1', ['--no-spec-split'], False),
    ]
    with tempfile.TemporaryDirectory(prefix='strata-no-model-') as td:
        missing = str(Path(td) / 'missing-pack')
        for enabled, flags, reject in cases:
            env['STRATA_ACCEPTED_USAGE'] = enabled
            command = [str(args.engine.resolve()), '--serve', '--pack', missing,
                       '--native', missing, '--ple-gguf', missing, *flags]
            result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=20)
            output = result.stdout + result.stderr
            guarded = 'STRATA_ACCEPTED_USAGE' in output and '--spec-split' in output
            print(f'accepted_usage={enabled} flags={flags} exit={result.returncode}\n{output}', flush=True)
            if reject:
                assert result.returncode == 2 and guarded, 'Unsafe combination was not rejected by its configuration guard'
            else:
                # A missing native-pack descriptor can reach the non-native CPU
                # feature check before the file-open error on an AVX2-only host.
                sentinel = missing in output or 'this CPU cannot run the expert kernel' in output
                assert result.returncode != 0 and not guarded and sentinel, 'Allowed mode did not reach the no-model sentinel'
    print('PASS accepted-usage split-window guard and allowed-mode controls')


if __name__ == '__main__':
    main()
