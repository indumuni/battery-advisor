from battery_advisor.models.requirements import Requirements
from battery_advisor.agent.clarifier import missing_must_haves, consistency_warnings, is_ready

def test_empty_needs_everything():
    assert len(missing_must_haves(Requirements())) == 4

def test_energy_derived_from_load_and_runtime():
    r = Requirements(application="e-bike", nominal_voltage_v=48, peak_load_w=750,
                     continuous_load_w=400, target_runtime_h=2)
    assert is_ready(r)

def test_energy_mismatch_warns():
    r = Requirements(continuous_load_w=400, target_runtime_h=2, required_energy_wh=2000)
    assert consistency_warnings(r)