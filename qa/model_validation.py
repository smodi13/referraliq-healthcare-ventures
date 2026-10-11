"""Independent validation for ReferralIQ model v2.0.0.
This is a pure Python reference engine that Phase 3 must match, not a copy of Excel formulas.
Run: python qa/model_validation.py
"""
import json, math, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'model_contract.json').read_text())

def evaluate(a):
    required=['pilot_monthly_cases','scale_monthly_cases','eligible_share','completion_rate','net_minutes_saved','loaded_hourly_cost','cash_realization','pilot_vendor_monthly','scale_vendor_monthly','scale_support_monthly','scale_audit_monthly','pilot_support_monthly','pilot_audit_monthly','pilot_setup','scale_rollout_setup','first_year_ramp','ramp_m1','ramp_m2','ramp_m3','exit_premoney_m','round_raise_m','investor_check_m','exit_arr_m','exit_rev_multiple','ownership_dilution','hold_years','equity_value_factor']
    for k in required:
        if k not in a or not isinstance(a[k],(float,int)) or not math.isfinite(a[k]):raise ValueError('Missing, invalid or nonfinite: '+k)
    if any(a[k]<0 for k in required):raise ValueError('Negative input not allowed')
    if any(a[k]>1 for k in ['eligible_share','completion_rate','cash_realization','first_year_ramp','ramp_m1','ramp_m2','ramp_m3','ownership_dilution','equity_value_factor']):raise ValueError('Share outside [0,1]')
    if a['investor_check_m']<=0 or a['hold_years']<=0 or a['exit_premoney_m']+a['round_raise_m']<=0:raise ValueError('Invalid venture denominator')
    if a['investor_check_m']>a['round_raise_m']:raise ValueError('Check exceeds total round')
    pilot_month=[]
    for k in ('ramp_m1','ramp_m2','ramp_m3'):
        eligible=a['pilot_monthly_cases']*a['eligible_share']
        completed=eligible*a['completion_rate']*a[k]
        staff_hrs=completed*a['net_minutes_saved']/60
        capacity=staff_hrs*a['loaded_hourly_cost']
        pilot_month.append(dict(eligible=eligible,completed=completed,hours=staff_hrs,capacity=capacity,cash=capacity*a['cash_realization']))
    pilot_gross=sum(x['capacity'] for x in pilot_month)
    pilot_savings=sum(x['cash'] for x in pilot_month)
    pilot_cost=3*(a['pilot_vendor_monthly']+a['pilot_support_monthly']+a['pilot_audit_monthly'])+a['pilot_setup']
    requests=a['scale_monthly_cases']*12
    completed=requests*a['eligible_share']*a['completion_rate']
    annual_capacity=completed*a['net_minutes_saved']/60*a['loaded_hourly_cost']
    annual_cash=annual_capacity*a['cash_realization']
    recurring=12*(a['scale_vendor_monthly']+a['scale_support_monthly']+a['scale_audit_monthly'])
    full_first_year_cost=recurring+a['scale_rollout_setup']
    equity_post=a['exit_premoney_m']+a['round_raise_m']
    ownership=a['investor_check_m']/equity_post
    final_ownership=ownership*(1-a['ownership_dilution'])
    equity_exit=a['exit_arr_m']*a['exit_rev_multiple']*a['equity_value_factor']
    gross_proceeds=final_ownership*equity_exit
    moic=gross_proceeds/a['investor_check_m']
    irr=moic**(1/a['hold_years'])-1 if moic>0 else -1
    return {'pilot_capacity':pilot_gross,'pilot_cash':pilot_savings,'pilot_cost':pilot_cost,'pilot_net':pilot_savings-pilot_cost,
            'runrate_capacity':annual_capacity,'runrate_cash':annual_cash,'recurring_cost':recurring,'runrate_net':annual_cash-recurring,
            'runrate_coverage':annual_cash/recurring if recurring else 0,'first_year_net':annual_cash*a['first_year_ramp']-full_first_year_cost,
            'breakeven_cash_realization':recurring/annual_capacity if annual_capacity else 0,
            'venture_post_money':equity_post,'venture_initial_ownership':ownership,'venture_exit_ownership':final_ownership,
            'venture_exit_equity':equity_exit,'venture_proceeds':gross_proceeds,'venture_moic':moic,'venture_irr':irr}

class ModelTests(unittest.TestCase):
    def test_reference_scenarios(self):
        expected={'Downside':(-66635.52,-150384,-196950.4,0.3214285714285714),'Base':(-39834,25776,-31268,2.971428571428572),'Upside':(-31610,347400,249500,13.5)}
        for name,exp in expected.items():
            r=evaluate(C['scenarios'][name])
            for key,e in zip(('pilot_net','runrate_net','first_year_net','venture_moic'),exp):
                with self.subTest(name=name,key=key):self.assertAlmostEqual(r[key],e,places=5)
    def test_zero_pilot_volume_still_pays_setup(self):
        a=dict(C['scenarios']['Base']);a['pilot_monthly_cases']=0
        r=evaluate(a)
        self.assertEqual(r['pilot_capacity'],0)
        self.assertEqual(r['pilot_net'],-r['pilot_cost'])
    def test_zero_cash_conversion_does_not_create_savings(self):
        a=dict(C['scenarios']['Base']);a['cash_realization']=0
        r=evaluate(a)
        self.assertEqual(r['runrate_cash'],0)
        self.assertLess(r['runrate_net'],0)
    def test_more_dilution_reduces_return(self):
        a=dict(C['scenarios']['Base']);a['ownership_dilution']=0
        b=dict(a);b['ownership_dilution']=0.6
        self.assertGreater(evaluate(a)['venture_moic'],evaluate(b)['venture_moic'])
    def test_vendor_price_can_flip_net(self):
        a=dict(C['scenarios']['Base']);a['scale_vendor_monthly']=14000
        self.assertLess(evaluate(a)['runrate_net'],0)
    def test_invalid_inputs_rejected(self):
        a=dict(C['scenarios']['Base']);a['eligible_share']=1.2
        with self.assertRaises(ValueError):evaluate(a)
    def test_zero_exit_return(self):
        a=dict(C['scenarios']['Base']);a['exit_arr_m']=0
        r=evaluate(a)
        self.assertEqual(r['venture_moic'],0)
        self.assertEqual(r['venture_irr'],-1)
    def test_check_cannot_exceed_round(self):
        a=dict(C['scenarios']['Base']);a['investor_check_m']=30
        with self.assertRaises(ValueError):evaluate(a)
    def test_scenario_order(self):
        r={k:evaluate(v) for k,v in C['scenarios'].items()}
        self.assertLess(r['Downside']['runrate_net'],r['Base']['runrate_net'])
        self.assertLess(r['Base']['runrate_net'],r['Upside']['runrate_net'])
        self.assertLess(r['Downside']['venture_moic'],r['Base']['venture_moic'])

if __name__=='__main__':
    fixtures={name:evaluate(a) for name,a in C['scenarios'].items()}
    (ROOT/'model_fixtures.json').write_text(json.dumps({'model_version':C['model_version'],'warning':'Illustrative model outputs only; not verified company results','scenarios':fixtures},indent=2))
    unittest.main(verbosity=2)
