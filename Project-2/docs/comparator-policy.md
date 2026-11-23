# Portfolio Comparator Policy

These comparisons use the same five funds, historical window, cost assumptions and rule checks as the selected portfolio.

- **Equal weight** puts 20% in each fund. It shows what a simple split would do without making return or risk estimates drive the weights.
- **Inverse volatility** gives more weight to funds whose historical returns moved less. Its weights are proportional to one divided by each fund’s estimated volatility. It does not account for how funds move together when setting the weights. The evaluation does account for those relationships when measuring total risk.

These comparisons help explain what the constraint-based search adds. Neither result establishes outperformance or suitability. The **60/40 policy benchmark** is 60% VTI and 40% IEF with annual rebalancing as specified in the [decision memo](decision-memo.md#6-benchmark). At the original inputs, the model estimates 7.17% annual return and 11.51% volatility using the same fixed-weight calculation. The report does not backtest annual rebalancing or drawdowns.
