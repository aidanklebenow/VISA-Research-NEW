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
    volatility_limit: float = .10  # Proposed research limit; not client approved.


def cpi_signal(as_of=AS_OF):
    if date.fromisoformat(as_of) < date(2026, 10, 30):
        raise ValueError('This vintage is eligible only from October 30, 2026; obtain an earlier vintage.')
    with (ROOT / 'data/cpi-vintage-2026-10-29.csv').open() as f:
        values = {r['date']: float(r['value']) for r in csv.DictReader(f)}
    end = max(values)
    prior = f'{int(end[:4])-1}{end[4:]}'
    return dict(measured=end, vintage='2026-10-29', eligible='2026-10-30',
                value=values[end], prior_value=values[prior],
                inflation_yoy=values[end]/values[prior]-1,
                role='Purchasing-power monitor only; does not alter weights or predict returns.')


def evaluate(name, weights, estimates, settings):
    vehicles, correlations = estimates['vehicles'], estimates['correlations']
    result = p.evaluate_mix(weights, vehicles, correlations, {'SGOV'})
    net = result['expected_return'] - settings.annual_cost
    rules = {
        'Long-only and fully invested': all(w >= 0 for w in weights) and abs(sum(weights)-1) < 1e-10,
        'Return estimate proxy meets target': net >= settings.target-1e-12,
        'SGOV reserve meets minimum': result['reserve_weight'] >= settings.reserve-1e-12,
        'Estimated volatility within proposed limit': result['volatility'] <= settings.volatility_limit+1e-12,
    }
    return dict(name=name, **result, net_return_proxy=net, rules=rules,
                model_verdict='PASS' if all(rules.values()) else 'FAIL',
                full_mandate_verdict='FAIL — mandate not established',
                unresolved=['7% issuer rule: ETF look-through, aggregation and Treasury exception undefined',
                            'Zero realized losses cannot be guaranteed',
                            'Arithmetic estimate does not establish 5-year compounded net target',
                            'Client risk limit, benchmark and withdrawal schedule not approved'])


def run(settings=Settings(), last_36=False, vti_shift=0):
    if not (0 <= settings.reserve <= 1 and 0 <= settings.annual_cost <= 1
            and 0 < settings.volatility_limit <= 1 and 0 <= settings.target <= 1):
        raise ValueError('Invalid mandate or cost settings.')
    estimates = p.estimate_from_csv(ROOT / 'data/prices.csv', last_36=last_36)
    estimates['vehicles'] = [(n, r + (vti_shift if n == 'VTI' else 0), s)
                             for n, r, s in estimates['vehicles']]
    names = [v[0] for v in estimates['vehicles']]
    results = [evaluate('Equal weight', p.equal_weights(estimates['vehicles']), estimates, settings),
               evaluate('Inverse volatility', p.inverse_volatility_weights(estimates['vehicles']), estimates, settings)]
    best = p.lowest_risk_mix(estimates['vehicles'], estimates['correlations'],
                            settings.target+settings.annual_cost, settings.reserve, {'SGOV'})
    if best:
        results.append(evaluate('Constrained portfolio', best['weights'], estimates, settings))
    return dict(as_of=AS_OF, settings=settings.__dict__, tickers=names, estimates=estimates,
                portfolios=results, feasible=bool(best), signal=cpi_signal(),
                status='RESEARCH ONLY — not approved for client allocation')


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
    artifact = dict(base=run(), stresses=stress_suite())
    target = ROOT / 'output/results.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(artifact, indent=2)+'\n')
    print(f'Executed historical research snapshot: {target}')
    for row in artifact['base']['portfolios']:
        print(row['name'], row['weights'], f"return proxy {row['net_return_proxy']:.2%}",
              f"volatility {row['volatility']:.2%}", row['model_verdict'], row['full_mandate_verdict'])
