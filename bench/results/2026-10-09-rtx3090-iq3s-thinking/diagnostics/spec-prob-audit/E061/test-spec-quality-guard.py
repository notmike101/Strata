import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('spec_quality_guard',Path(__file__).with_name('spec-quality-guard.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class GuardTests(unittest.TestCase):
    def test_retained_control(self):
        m.require_spec_quality({'env':{},'args':['--spec','4','--spec-min-p','0.70']})
    def test_nonzero_environment_values_match_engine(self):
        for enabled in ['yes','true','2',1]:
            with self.subTest(enabled=enabled), self.assertRaisesRegex(ValueError,'distribution-top'):
                m.require_spec_quality({'env':{'STRATA_SPEC_PROB':enabled},'args':['--suffix-draft','0']})
    def test_reject_picked_token_gate(self):
        with self.assertRaisesRegex(ValueError,'distribution-top'):
            m.require_spec_quality({'env':{'STRATA_SPEC_PROB':'1'},'args':['--suffix-draft','0']})
    def test_reject_draft_dependent_suffix_selection(self):
        with self.assertRaisesRegex(ValueError,'suffix'):
            m.require_spec_quality({'env':{'STRATA_SPEC_PROB':'1','STRATA_SPEC_PROB_GATE':'top'},'args':[]})
    def test_accept_audited_configuration(self):
        m.require_spec_quality({'env':{'STRATA_SPEC_PROB':'1','STRATA_SPEC_PROB_GATE':'top'},'args':['--suffix-draft','0']})
    def test_reject_unaudited_lookup_chain(self):
        with self.assertRaisesRegex(ValueError,'lookup chain'):
            m.require_spec_quality({'env':{'STRATA_SPEC_PROB':'1','STRATA_SPEC_PROB_GATE':'top'},'args':['--suffix-draft','0','--lookup-chain','2']})
unittest.main()
