import importlib.util,os,unittest
from unittest.mock import patch
from pathlib import Path
s=importlib.util.spec_from_file_location('spec_quality_guard',Path(__file__).with_name('spec-quality-guard.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class GuardTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
    def test_inherited_probabilistic_mode_is_checked(self):
        with patch.dict(os.environ, {'STRATA_SPEC_PROB': '1'}):
            with self.assertRaisesRegex(ValueError, 'distribution-top'):
                m.require_spec_quality({'args': ['--suffix-draft', '0']})
    def test_explicit_disable_overrides_inherited_mode(self):
        with patch.dict(os.environ, {'STRATA_SPEC_PROB': '1'}):
            m.require_spec_quality({'env': {'STRATA_SPEC_PROB': 0}})
    def test_inherited_gate_is_used_with_config_enablement(self):
        with patch.dict(os.environ, {'STRATA_SPEC_PROB_GATE': 'top'}):
            m.require_spec_quality({'env': {'STRATA_SPEC_PROB': 1}, 'args': ['--suffix-draft', '0']})
    def test_config_gate_overrides_inherited_gate(self):
        with patch.dict(os.environ, {'STRATA_SPEC_PROB': '1', 'STRATA_SPEC_PROB_GATE': 'top'}):
            with self.assertRaisesRegex(ValueError, 'distribution-top'):
                m.require_spec_quality({'env': {'STRATA_SPEC_PROB_GATE': 'pick'}, 'args': ['--suffix-draft', '0']})
    def test_retained_control(self):
        m.require_spec_quality({'env':{},'args':['--spec','4','--spec-min-p','0.70']})
    def test_manifest_records_effective_modes_only(self):
        with patch.dict(os.environ, {'STRATA_SPEC_PROB': '1', 'STRATA_API_KEY': 'synthetic-secret'}):
            manifest = m.sampling_mode_manifest({'env': {'STRATA_SPEC_PROB': 0}})
        self.assertEqual(manifest['STRATA_SPEC_PROB'], '0')
        self.assertIsNone(manifest['STRATA_OLD_SAMPLER'])
        self.assertEqual(set(manifest), set(m.SAMPLING_MODE_KEYS))
        self.assertNotIn('synthetic-secret', str(manifest))
    def test_windows_noncanonical_mode_keys_are_rejected(self):
        with patch.object(os, 'name', 'nt'):
            for env in [{'strata_spec_prob': '1'}, {'STRATA_SPEC_PROB': '0', 'strata_spec_prob': '1'}, {'Strata_Spec_Prob_Gate': 'top'}]:
                with self.subTest(env=env), self.assertRaisesRegex(ValueError, 'canonical uppercase'):
                    m.require_spec_quality({'env': env})
    def test_last_duplicate_value_controls_validation(self):
        env = {'STRATA_SPEC_PROB': '1', 'STRATA_SPEC_PROB_GATE': 'top'}
        for flag, error in [('--suffix-draft', 'suffix'), ('--lookup-chain', 'lookup chain')]:
            with self.subTest(flag=flag, last='unsafe'), self.assertRaisesRegex(ValueError, error):
                m.require_spec_quality({'env': env, 'args': ['--suffix-draft', '0', flag, '0', flag, '3']})
            with self.subTest(flag=flag, last='safe'):
                m.require_spec_quality({'env': env, 'args': ['--suffix-draft', '0', flag, '3', flag, '0']})
    def test_missing_relevant_flag_value_is_rejected(self):
        env = {'STRATA_SPEC_PROB': '1', 'STRATA_SPEC_PROB_GATE': 'top'}
        for flag in ['--suffix-draft', '--lookup-chain']:
            for tail in [[], ['--spec', '4']]:
                with self.subTest(flag=flag, tail=tail), self.assertRaisesRegex(ValueError, 'Missing value'):
                    m.require_spec_quality({'env': env, 'args': ['--suffix-draft', '0', flag] + tail})
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
