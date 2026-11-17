"""Lab 14 portfolio baselines. Standard library only; inputs use decimals.

From the workspace root: python3 model/src/portfolio.py
Course-authored training inputs, not current market estimates.
"""
from math import isclose, isfinite, sqrt
import csv
from datetime import date
from io import StringIO
from pathlib import Path
from statistics import mean, stdev, correlation

# Order is shared by the correlation matrix and every weight vector.
VEHICLES = [
    ('Treasury bills', 0.035, 0.005),
    ('Treasury 10-year note', 0.043, 0.07),
    ('Investment-grade bond fund', 0.05, 0.06),
    ('Global equity index fund', 0.08, 0.16),
]
CORRELATIONS = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
]
OBJECTIVE = 0.065  # CPI estimate 2.5% + 4 percentage points.
RESERVE_ELIGIBLE = {'Treasury bills', 'Treasury 10-year note'}

# EDIT YOUR WEIGHTS HERE. Enter percentages: 25 means 25%, not 0.25.
# These four numbers must add up to 100. Starting example, not a recommendation.
SHOW_CUSTOM_PORTFOLIO = False  # Set True for experiments; lab prints three baselines.
CUSTOM_WEIGHTS_PERCENT = {
    'Treasury bills': 25.0,
    'Treasury 10-year note': 25.0,
    'Investment-grade bond fund': 25.0,
    'Global equity index fund': 25.0,
}


def custom_weights(vehicles):
    if set(CUSTOM_WEIGHTS_PERCENT) != {name for name, _, _ in vehicles}:
        raise ValueError('Custom weights must name exactly the four investment vehicles.')
    weights = [CUSTOM_WEIGHTS_PERCENT[name] / 100 for name, _, _ in vehicles]
    validate_weights(weights, len(vehicles))
    return weights


def validate_inputs(vehicles, correlations):
    n = len(vehicles)
    if not n or len({v[0] for v in vehicles}) != n:
        raise ValueError('Investment vehicle names must be unique and nonempty.')
    if any(not isfinite(r) or not isfinite(s) or s <= 0 for _, r, s in vehicles):
        raise ValueError('Returns must be finite and volatilities finite and positive.')
    if len(correlations) != n or any(len(row) != n for row in correlations):
        raise ValueError('Correlation table must have one row and column per vehicle.')
    for i in range(n):
        for j in range(n):
            value = correlations[i][j]
            if not isfinite(value) or not -1 <= value <= 1:
                raise ValueError(f'Correlation [{i}][{j}] must be between -1 and 1.')
            if not isclose(value, correlations[j][i], rel_tol=0, abs_tol=1e-12):
                raise ValueError('Correlation table must be symmetric; edit both cells.')
        if not isclose(correlations[i][i], 1, rel_tol=0, abs_tol=1e-12):
            raise ValueError('Each diagonal correlation must equal 1.')


def covariance_matrix(vehicles, correlations):
    validate_inputs(vehicles, correlations)
    return [[correlations[i][j] * vehicles[i][2] * vehicles[j][2]
             for j in range(len(vehicles))] for i in range(len(vehicles))]


def equal_weights(vehicles):
    return [1 / len(vehicles)] * len(vehicles)


def inverse_volatility_weights(vehicles):
    inverse = [1 / volatility for _, _, volatility in vehicles]
    total = sum(inverse)
    return [value / total for value in inverse]


def validate_weights(weights, size):
    if len(weights) != size or any(not isfinite(w) or w < 0 for w in weights):
        raise ValueError('Supply one finite, nonnegative weight per vehicle.')
    if not isclose(sum(weights), 1, rel_tol=0, abs_tol=1e-10):
        raise ValueError('Weights must sum to 1 (100%).')


def expected_return(weights, vehicles):
    validate_weights(weights, len(vehicles))
    return sum(weight * vehicle[1] for weight, vehicle in zip(weights, vehicles))


def portfolio_volatility(weights, covariance):
    validate_weights(weights, len(covariance))
    # Include EVERY pair i,j: diagonal terms are individual variances;
    # off-diagonal terms include each pair twice, providing the familiar 2ab term.
    variance = sum(weights[i] * weights[j] * covariance[i][j]
                   for i in range(len(weights)) for j in range(len(weights)))
    if variance < -1e-12:
        raise ValueError('Negative portfolio variance: check the covariance inputs.')
    return sqrt(max(0, variance))


def reserve_weight(weights, vehicles):
    validate_weights(weights, len(vehicles))
    return sum(w for w, vehicle in zip(weights, vehicles)
               if vehicle[0] in RESERVE_ELIGIBLE)


def meets_objective(portfolio_return, objective):
    return portfolio_return >= objective - 1e-12


def baseline_weights(vehicles):
    benchmark = {'Investment-grade bond fund': 0.4, 'Global equity index fund': 0.6}
    return {'Benchmark': [benchmark.get(name, 0) for name, _, _ in vehicles],
            'Equal weight': equal_weights(vehicles),
            'Inverse volatility': inverse_volatility_weights(vehicles)}


def lowest_risk_mix(vehicles, correlations, objective=OBJECTIVE,
                    reserve_minimum=0.03, reserve_eligible=None):
    """Exhaust every long-only allocation on a 5-percentage-point grid.

    Returns weights and calculated metrics, or None when infeasible.
    Inputs/outputs use decimals; eligibility is a set of asset names.
    """
    covariance = covariance_matrix(vehicles, correlations)
    if not 3 <= len(vehicles) <= 6:
        raise ValueError('Supply three to six assets for the grid search.')
    if not isfinite(objective):
        raise ValueError('The objective must be finite.')
    if not isfinite(reserve_minimum) or not 0 <= reserve_minimum <= 1:
        raise ValueError('Reserve minimum must be between 0 and 100%.')
    eligible = set(RESERVE_ELIGIBLE if reserve_eligible is None else reserve_eligible)
    if eligible - {v[0] for v in vehicles}:
        raise ValueError('Reserve eligibility contains an unknown asset.')

    def allocations(remaining, count):
        # Twenty units of 5% must be assigned, so every mix sums to 100%.
        if count == 1:
            yield [remaining / 20]
        else:
            for units in range(remaining + 1):
                for rest in allocations(remaining - units, count - 1):
                    yield [units / 20] + rest

    best = None
    for weights in allocations(20, len(vehicles)):
        result = expected_return(weights, vehicles)
        reserve = sum(w for w, asset in zip(weights, vehicles) if asset[0] in eligible)
        if not meets_objective(result, objective) or reserve < reserve_minimum - 1e-12:
            continue
        volatility = portfolio_volatility(weights, covariance)
        if best is None or volatility < best['volatility']:
            best = dict(weights=weights, expected_return=result,
                        volatility=volatility, reserve_weight=reserve)
    return best


def estimate_from_csv(source, last_36=False):
    """Read monthly adjusted prices; estimate annual mean, sample risk, correlation.

    Accepts a path or an uploaded text/binary file. Rejects missing data instead
    of silently filling or dropping it. The last-36 switch selects RETURNS,
    retaining the preceding price needed for the first selected return.
    """
    content = source.read() if hasattr(source, 'read') else Path(source).read_bytes()
    if isinstance(content, bytes):
        content = content.decode('utf-8-sig')
    rows = list(csv.reader(StringIO(content)))
    if not rows:
        raise ValueError('CSV is empty.')
    header = [cell.strip() for cell in rows[0]]
    names = header[1:]
    if not 3 <= len(names) <= 6 or any(not name for name in names) or len(set(names)) != len(names):
        raise ValueError('CSV needs a date column followed by three to six unique tickers.')
    dates, prices = [], []
    for line, row in enumerate(rows[1:], 2):
        if len(row) != len(header):
            raise ValueError(f'CSV row {line}: missing or extra columns.')
        try:
            observed = date.fromisoformat(row[0].strip())
            values = [float(cell) for cell in row[1:]]
        except ValueError as error:
            raise ValueError(f'CSV row {line}: use YYYY-MM-DD and numeric prices.') from error
        if any(not isfinite(value) or value <= 0 for value in values):
            raise ValueError(f'CSV row {line}: prices must be finite and positive.')
        if dates:
            previous_month = dates[-1].year * 12 + dates[-1].month
            if observed.year * 12 + observed.month != previous_month + 1:
                raise ValueError('Dates must be oldest first, one observation per consecutive month.')
        dates.append(observed)
        prices.append(values)
    if len(prices) < 3:
        raise ValueError('At least three monthly prices are needed for sample statistics.')
    returns = [[current[i] / previous[i] - 1 for i in range(len(names))]
               for previous, current in zip(prices, prices[1:])]
    if last_36 and len(returns) < 36:
        raise ValueError('The last-36-months estimate needs at least 37 monthly prices.')
    selected = returns[-36:] if last_36 else returns
    columns = list(zip(*selected))
    if any(stdev(column) == 0 for column in columns):
        raise ValueError('An asset has zero return variation; its correlation is undefined.')
    vehicles = [(name, mean(column) * 12, stdev(column) * sqrt(12))
                for name, column in zip(names, columns)]
    correlations = [[1.0 if i == j else max(-1.0, min(1.0, correlation(a, b)))
                     for j, b in enumerate(columns)] for i, a in enumerate(columns)]
    validate_inputs(vehicles, correlations)
    return dict(vehicles=vehicles, correlations=correlations, months=len(selected),
                price_start=dates[-len(selected) - 1].isoformat(),
                price_end=dates[-1].isoformat())


def evaluate_mix(weights, vehicles, correlations, reserve_eligible):
    """Evaluate a manual allocation with the same math used by the optimizer."""
    validate_weights(weights, len(vehicles))
    return dict(weights=list(weights), expected_return=expected_return(weights, vehicles),
                volatility=portfolio_volatility(weights, covariance_matrix(vehicles, correlations)),
                reserve_weight=sum(w for w, asset in zip(weights, vehicles)
                                   if asset[0] in reserve_eligible))


def rebalance_weights_percent(weights, index, new_weight):
    """Move one integer-percent dial; distribute the remainder across other assets.

    Preserve their relative proportions, using largest-remainder rounding so the
    total stays exactly 100. If all other assets were zero, split evenly.
    """
    if len(weights) < 2 or not 0 <= index < len(weights):
        raise ValueError('Choose a valid asset in a portfolio with at least two assets.')
    if any(not isinstance(w, int) or w < 0 for w in weights) or sum(weights) != 100:
        raise ValueError('Dial weights must be nonnegative integers totaling 100.')
    if not isinstance(new_weight, int) or not 0 <= new_weight <= 100:
        raise ValueError('Dial must be between 0 and 100%.')
    others = [i for i in range(len(weights)) if i != index]
    total = sum(weights[i] for i in others)
    remaining = 100 - new_weight
    exact = {i: remaining * weights[i] / total if total else remaining / len(others)
             for i in others}
    result = [0] * len(weights)
    result[index] = new_weight
    for i in others:
        result[i] = int(exact[i])
    for i in sorted(others, key=lambda i: exact[i] - result[i], reverse=True)[:100 - sum(result)]:
        result[i] += 1
    return result


def report():
    covariance = covariance_matrix(VEHICLES, CORRELATIONS)
    lines = ['Lab 14 — course training inputs', f'Objective: {OBJECTIVE:.2%}']
    portfolios = baseline_weights(VEHICLES)
    if SHOW_CUSTOM_PORTFOLIO:
        portfolios['My custom portfolio'] = custom_weights(VEHICLES)
    for name, weights in portfolios.items():
        result = expected_return(weights, VEHICLES)
        lines.extend(['', name])
        lines.extend(f'  {vehicle[0]}: {weight:.1%}'
                     for weight, vehicle in zip(weights, VEHICLES))
        lines.extend([f'  Expected return: {result:.2%}',
                      f'  Volatility: {portfolio_volatility(weights, covariance):.2%}',
                      f'  Reserve-eligible: {reserve_weight(weights, VEHICLES):.1%}',
                      f'  Meets objective: {"yes" if meets_objective(result, OBJECTIVE) else "no"}'])
    return '\n'.join(lines)


if __name__ == '__main__':
    try:
        print(report())
    except ValueError as error:
        raise SystemExit(f'Input error: {error}')
