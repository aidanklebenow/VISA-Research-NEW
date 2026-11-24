"""Offline research snapshot. No trading, forecasting guarantee, or AI service."""
import csv
import json
from datetime import date
from pathlib import Path
from dataclasses import dataclass
import portfolio as p

ROOT = Path(__file__).resolve().parent
AS_OF = '2026-10-30'


@dataclass(frozen=True)
class Settings:
    target: float = .075
    reserve: float = .10
    annual_cost: float = 0
    volatility_limit: float = .10  # Aidan’s policy limit for the original case.


def available_return_months():
    """Count bundled price observations, allowing one for the first return."""
    with (ROOT / 'data/prices.csv').open(encoding='utf-8-sig', newline='') as source:
        prices = csv.reader(source)
        next(prices, None)
        return max(0, sum(bool(row) for row in prices) - 1)


# REQ[P2-04]: Date-gated inflation signal | Rubric: Data integrity and traceability | Evidence: test_vintage_gate_and_same_vintage_calculation
def cpi_signal(as_of=AS_OF):
    if date.fromisoformat(as_of) < date(2026, 10, 30):
        raise ValueError('This vintage is eligible only from October 30, 2026; obtain an earlier vintage.')
    with (ROOT / 'data/cpi-vintage-2026-10-29.csv').open() as f:
        values = {r['date']: float(r['value']) for r in csv.DictReader(f)}
    if not values:
        raise ValueError('The CPI vintage is empty.')
    end = max(values)
    prior = f'{int(end[:4])-1}{end[4:]}'
    return dict(measured=end, vintage='2026-10-29', eligible='2026-10-30',
                value=values[end], prior_value=values[prior],
                inflation_yoy=values[end]/values[prior]-1,
                role='Purchasing-power monitor only; does not alter weights or predict returns.')


def evaluate(name, weights, estimates, settings, max_weights=None):
    vehicles, correlations = estimates['vehicles'], estimates['correlations']
    result = p.evaluate_mix(weights, vehicles, correlations, {'SGOV'})
    net = result['expected_return'] - settings.annual_cost
    rules = {
        'Long-only and fully invested': all(w >= 0 for w in weights) and abs(sum(weights)-1) < 1e-10,
        'Return estimate proxy meets target': net >= settings.target-1e-12,
        'SGOV reserve meets minimum': result['reserve_weight'] >= settings.reserve-1e-12,
        'Estimated volatility within proposed limit': result['volatility'] <= settings.volatility_limit+1e-12,
    }
    if max_weights is not None:
        rules['Fund maximums and exclusions respected'] = all(
            weight <= cap + 1e-12 for weight, cap in zip(weights, max_weights))
    return dict(name=name, **result, net_return_proxy=net, rules=rules,
                model_verdict='PASS' if all(rules.values()) else 'FAIL',
                full_mandate_verdict='FAIL — five-year compounded growth not established',
                mandate_policy={'issuer_rule': '7% look-through cap on corporate holdings; U.S. Treasuries exempt',
                                'liquidity_rule': 'Minimum 10% in SGOV replaces the zero-loss rule',
                                'benchmark': '60% VTI / 40% IEF, rebalanced annually',
                                'risk_limit': '10% annual volatility', 'withdrawals': '$4,000 per year, taken quarterly'},
                unresolved=['The arithmetic estimate does not prove five-year compounded growth'])


def run(settings=Settings(), last_36=False, vti_shift=0, *,
        history_months=None, fund_limits=None, vxus_shift=0):
    if not (0 <= settings.reserve <= 1 and 0 <= settings.annual_cost <= 1
            and 0 < settings.volatility_limit <= 1 and 0 <= settings.target <= 1):
        raise ValueError('Invalid mandate or cost settings.')
    for filename in ('price-sources.json', 'macro-download-manifest.json'):
        source = ROOT / 'data' / filename
        if not json.loads(source.read_text(encoding='utf-8')):
            raise ValueError(f'Empty source record: {filename}')
    estimates = p.estimate_from_csv(ROOT / 'data/prices.csv', last_36=last_36,
                                    history_months=history_months)
    shifts = {'VTI': vti_shift, 'VXUS': vxus_shift}
    vehicles = [(n, r + shifts.get(n, 0), s) for n, r, s in estimates['vehicles']]
    estimates['vehicles'] = vehicles
    names = [v[0] for v in vehicles]
    limits = [fund_limits.get(name, 1) for name in names] if fund_limits is not None else None
    if limits is not None and any(not 0 <= limit <= 1 for limit in limits):
        raise ValueError('Fund limits must be between 0% and 100%.')
    included = [i for i in range(len(names)) if limits is None or limits[i] > 0]
    if not included:
        raise ValueError('Include at least one fund with a maximum above 0%.')
    included_vehicles = [vehicles[i] for i in included]
    results = []
    for label, comparator in [('Equal weight', p.equal_weights),
                              ('Inverse volatility', p.inverse_volatility_weights)]:
        weights = [0.] * len(names)
        for i, weight in zip(included, comparator(included_vehicles)):
            weights[i] = weight
        results.append(evaluate(label, weights, estimates, settings, limits))
    best = p.lowest_risk_mix(vehicles, estimates['correlations'],
                            settings.target+settings.annual_cost, settings.reserve, {'SGOV'},
                            max_weights=limits)
    if best:
        results.append(evaluate('Constrained portfolio', best['weights'], estimates, settings, limits))
    return dict(as_of=AS_OF, settings=settings.__dict__, tickers=names, estimates=estimates,
                portfolios=results, feasible=bool(best), signal=cpi_signal(),
                status='RESEARCH MODEL — committee recommendation recorded in the decision memo')


# REQ[P2-05]: Stress estimates, window, costs and rules | Rubric: Validation, sensitivity, and reproducibility | Evidence: output/results.json
def stress_suite():
    scenarios = [('Base', Settings(), False, 0),
                 ('VTI estimate lower by 1 percentage point', Settings(), False, -.01),
                 ('Last 36 monthly returns', Settings(), True, 0),
                 ('Annual investor cost 0.50%', Settings(annual_cost=.005), False, 0),
                 ('Reserve floor 30%', Settings(reserve=.30), False, 0),
                 ('Volatility ceiling 5%', Settings(volatility_limit=.05), False, 0)]
    rows = []
    for label, settings, short, shift in scenarios:
        result = run(settings, short, shift)
        selected = next((r for r in result['portfolios'] if r['name']=='Constrained portfolio'), None)
        rows.append(dict(scenario=label, settings=settings.__dict__, last_36=short,
                         vti_shift=shift, result=selected,
                         stop=selected is None or selected['model_verdict']=='FAIL'))
    return rows


# REQ[P2-09]: Centered sensitivity grid | Rubric: Validation, sensitivity, and reproducibility | Evidence: test_sensitivity_grid_center_and_invalid_cells
def sensitivity_grid():
    """Compare return targets and risk ceilings around the published settings."""
    cases = []
    for target in (.05, Settings.target, .15):
        # A ceiling affects the verdict only, so one search suffices per target.
        result = run(Settings(target=target))
        candidate = next((row for row in result['portfolios'] if row['name'] == 'Constrained portfolio'), None)
        volatility = candidate['volatility'] if candidate else None
        cases.append({
            'target': target,
            'cells': [
                {'limit': limit, 'volatility': volatility,
                 'verdict': ('No mix' if volatility is None else
                             'Above limit' if volatility > limit + 1e-12 else 'Pass')}
                for limit in (.05, Settings.volatility_limit, .15)
            ],
        })
    return cases


def research_prompt(question, snapshot):
    return ('Educational investment research. Separate facts, calculations and suggestions. '
            'Cite dated primary sources. Do not invent holdings or recommend a trade. '
            'This is a historical research portfolio, not a verified client account. '
            'Tesla is not a direct holding in this five-fund model; indirect fund exposure is unverified. '
            'For a Tesla comparison, first obtain actual holdings, weights, horizon, risk limits, '
            'tax/account type and mandate permissions. Compare keep/reduce/replace conditionally. '
            'Explain concentration, diversification, volatility, drawdowns, correlations, fees and taxes. '
            'Mutual funds are not automatically safer; lower risk does not guarantee higher returns. '
            'Do not treat the arithmetic historical estimate as a forecast.\n\n'
            + 'Question: ' + question + '\n\nVerified local calculation snapshot:\n'
            + json.dumps(snapshot, indent=2))


if __name__ == '__main__':
    artifact = dict(base=run(), stresses=stress_suite(), sensitivity=sensitivity_grid())
    target = ROOT / 'output/results.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(artifact, indent=2)+'\n')
    print(f'Executed historical research snapshot: {target}')
    for row in artifact['base']['portfolios']:
        print(row['name'], row['weights'], f"return proxy {row['net_return_proxy']:.2%}",
              f"volatility {row['volatility']:.2%}", row['model_verdict'], row['full_mandate_verdict'])
