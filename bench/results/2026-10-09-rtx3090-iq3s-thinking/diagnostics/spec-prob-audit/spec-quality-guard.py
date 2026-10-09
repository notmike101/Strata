"""Reject speculative candidates known to fail target-distribution preservation."""
def require_spec_quality(candidate):
    env=candidate.get('env',{})
    if env.get('STRATA_SPEC_PROB')!='1':
        return
    if env.get('STRATA_SPEC_PROB_GATE')!='top':
        raise ValueError('Speculative rejection requires distribution-top gating; picked-token gating is biased')
    args=candidate.get('args',[])
    def flag(name,default):
        return args[args.index(name)+1] if name in args else default
    if flag('--suffix-draft','1')!='0':
        raise ValueError('Speculative rejection requires suffix drafting disabled; draft-dependent source selection is biased')
    if flag('--lookup-chain','0')!='0':
        raise ValueError('Speculative rejection lookup chain has not passed the integration audit')
