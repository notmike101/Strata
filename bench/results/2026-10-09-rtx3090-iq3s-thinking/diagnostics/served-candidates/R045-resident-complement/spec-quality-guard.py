"""Reject speculative candidates known to fail target-distribution preservation."""
import os

# Only these values may enter the published run manifest. Never log os.environ.
SAMPLING_MODE_KEYS = (
    'STRATA_SPEC_PROB', 'STRATA_SPEC_PROB_GATE', 'STRATA_SPEC_MIN_TEMP',
    'STRATA_SPEC_PROB_DT', 'STRATA_SPEC_GUMBEL', 'STRATA_SPEC_COUPLED',
    'STRATA_OLD_SAMPLER', 'STRATA_SAMPLER_ONE_BLOCK',
)


def effective_environment(candidate):
    """Match serve.server's inherited environment plus stringified config overlay."""
    env = dict(os.environ)
    env.update({str(k): str(v) for k, v in (candidate.get('env') or {}).items()})
    return env


def sampling_mode_manifest(candidate):
    env = effective_environment(candidate)
    return {key: env.get(key) for key in SAMPLING_MODE_KEYS}


def require_spec_quality(candidate):
    env=effective_environment(candidate)
    # Match spec_prob_env(): every nonempty value except the exact string "0" enables it.
    if str(env.get('STRATA_SPEC_PROB','')) in ('','0'):
        return
    if env.get('STRATA_SPEC_PROB_GATE')!='top':
        raise ValueError('Speculative rejection requires distribution-top gating; picked-token gating is biased')
    args=candidate.get('args',[])
    def flag(name,default):
        value = default
        for index, item in enumerate(args):
            if item == name:
                if index + 1 == len(args) or str(args[index + 1]).startswith('--'):
                    raise ValueError('Missing value for ' + name)
                value = str(args[index + 1])
        return value
    if flag('--suffix-draft','1')!='0':
        raise ValueError('Speculative rejection requires suffix drafting disabled; draft-dependent source selection is biased')
    if flag('--lookup-chain','0')!='0':
        raise ValueError('Speculative rejection lookup chain has not passed the integration audit')
