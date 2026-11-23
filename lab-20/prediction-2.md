Project 2 - Locked Changed-Input Prediction

1. What I'm changing:

Raising the minimum SGOV reserve from 10% to 60%. Every other input stays at the original case.

2. Before -> after:

Minimum SGOV reserve: 10% -> 60%

3. What I expect to happen to the mix:

SGOV goes up from 55% to 60%. Since total allocation has to equal 100%, that extra 5% has to come out of the equity sleeve (45% combined VTI and VXUS), dropping total stocks down to 40%. I expect VTI to drop from 30% to roughly 26–27% and VXUS to drop from 15% to roughly 13–14% (or VXUS taking the bulk of the cut down to ~10% while VTI holds around 30% to protect return).

4. What I expect to happen to return and volatility:

Return: Down, about 7.0%–7.2%
Volatility: Down, about 6.1%–6.3%
Why: Forcing 60% into low-yielding T-bills leaves only 40% for equities, which cuts portfolio risk below the baseline 6.8% but removes too much equity exposure to reach the 7.5% return hurdle.

5. Will it still pass, and does my recommendation change?

Fail — it will fail the 7.5% expected annual return rule (4 of 5 checks passed).
Yes, my recommendation changes from initiating the allocation to holding off or adjusting the client's return target, because a mandatory 60% cash reserve prevents the portfolio from mathematically hitting the required 7.5% growth goal.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

RESULTS:

R1. What actually happened?

The app failed to find any valid portfolio mix and displayed a red alert banner reading: "No grid portfolio meets the return target, cash reserve and fund limits." Because no mix satisfied all the rules simultaneously, the Expected Annual Return, Volatility, and Rule Checks cards all came back blank with dashes ("—").

R2. Was my prediction right?

My prediction was right on the core outcome: I predicted the portfolio would fail the 7.5% expected annual return rule because forcing 60% into SGOV leaves only 40% for equities, which isn't enough to hit the 7.5% hurdle. Where it differed was that instead of outputting a failing mix (like 60% SGOV / ~27% VTI / ~13% VXUS at ~7.0%–7.2% return and ~6.1%–6.3% volatility), the app's grid optimizer refused to display any portfolio at all and left the metric cards blank once no valid solution existed.

R3. Why did this happen?

With 60% locked into SGOV earning roughly 3.7% a year (contributing only 2.22% to total return), the remaining 40% would need to earn at least 13.2% per year just to reach the 7.5% target. Because VTI (~13.1%) and VXUS (~10.1%) fall short of 13.2%—and IEF and LQD have negative estimated returns—it is mathematically impossible for any combination of the remaining funds to hit 7.5% without breaching the 60% SGOV floor.

R4. What is the actual decision effect?

This result does not change my base recommendation (55% SGOV / 30% VTI / 15% VXUS), which already sits at the upper ceiling of how much cash the portfolio can hold while still clearing the 7.5% return hurdle: 55% is the highest SGOV level that works on the app's 5% grid (about 59.8% in theory if the rest of the portfolio were all VTI). If a client insisted on holding 60% in cash, I would explain that 60% SGOV and a 7.5% return target cannot coexist with these funds—so we would either keep the 10% minimum cash reserve (letting the optimizer stay at 55% SGOV) or lower the client's annual return goal to roughly 7.0%–7.2%.