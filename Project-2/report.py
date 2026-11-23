"""Presentation helpers for the allocation report."""
from html import escape

import plotly.graph_objects as go
import streamlit as st

import portfolio

FUNDS = {
    'SGOV': ('Short-term U.S. Treasury bills', 'Treasury bills', '#203e71'),
    'IEF': ('Intermediate-term U.S. Treasury bonds', 'U.S. Treasury bonds', '#77879f'),
    'LQD': ('Investment-grade company bonds', 'company bonds', '#a9b7cc'),
    'VTI': ('Broad U.S. stock market', 'U.S. stocks', '#357db1'),
    'VXUS': ('Broad stock markets outside the U.S.', 'international stocks', '#54a4a3'),
}
GOALS = (.06, .07, .075, .08, .09)
CEILINGS = (.06, .08, .10, .12)
CHART_CONFIG = {'displayModeBar': False, 'scrollZoom': False}


def percent(value):
    return f'{value:.1%}'


def dollars(value):
    return f'${value:,.0f}'


def section(number, title):
    st.html(f'<span class="eyebrow">{number:02d} · {escape(title)}</span>')
    st.header(title, anchor=title.lower().replace(' & ', '-').replace(' ', '-'))


def placeholder():
    return '<span class="placeholder">[AIDAN TO DECIDE]</span>'


def table(headers, rows, *, classes=None, label=None):
    """Render compact, accessible tables, with markup supplied by the report."""
    headings = ''.join(f'<th scope="col">{escape(title)}</th>' for title in headers)
    body = []
    for i, row in enumerate(rows):
        cells = []
        for j, value in enumerate(row):
            css = classes.get((i, j), '') if classes else ''
            cells.append(f'<td class="{css}">{value}</td>')
        body.append('<tr>' + ''.join(cells) + '</tr>')
    aria = f' aria-label="{escape(label)}"' if label else ''
    st.html(f'<div class="report-table"><table{aria}><thead><tr>{headings}</tr></thead>'
            '<tbody>' + ''.join(body) + '</tbody></table></div>')


def fund_mark(ticker):
    return f'<span class="fund-dot" style="background:{FUNDS[ticker][2]}"></span>{ticker}'


def mix_text(weights, names):
    return ' / '.join(f'{ticker} {percent(weight)}'
                      for ticker, weight in zip(names, weights) if weight > 0)


def cap_error(limits):
    if sum(limits.values()) < 1 - 1e-12:
        return 'The maximum weights of the included funds add up to less than 100.0%. Raise a maximum or include another fund.'
    return None


def style(dark):
    palette = {
        'bg': '#0c1423', 'paper': '#121e30', 'soft': '#192a42', 'ink': '#e8effb',
        'muted': '#aebed5', 'line': '#334869', 'accent': '#86c5ed',
        'pass': '#b8ebce', 'pass-bg': '#213d35', 'fail': '#ffd1d1', 'fail-bg': '#482a34',
        'caution': '#fbd99b', 'caution-bg': '#463822',
    } if dark else {
        'bg': '#f4f7fb', 'paper': '#ffffff', 'soft': '#e9f0f8', 'ink': '#172c4b',
        'muted': '#48617c', 'line': '#d3deeb', 'accent': '#235b9e',
        'pass': '#0c5c3a', 'pass-bg': '#e7f4ec', 'fail': '#982c39', 'fail-bg': '#ffedf0',
        'caution': '#714306', 'caution-bg': '#fff0d2',
    }
    variables = ';'.join(f'--pt-{key}:{value}' for key, value in palette.items())
    st.html(f"""
<style>
[data-testid="stApp"] {{{variables}; background:var(--pt-bg); color:var(--pt-ink);}}
[data-testid="stHeader"] {{background:var(--pt-bg); color:var(--pt-ink);}}
[data-testid="stToolbar"], footer {{display:none;}}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {{background:var(--pt-bg);}}
[data-testid="stSidebar"] {{background:var(--pt-paper); border-right:1px solid var(--pt-line);}}
[data-testid="stApp"] :is(h1,h2,h3,p,label,summary,li) {{color:var(--pt-ink);}}
[data-testid="stApp"] a {{color:var(--pt-accent);}}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{
  color:var(--pt-muted); opacity:1;
}}
[data-testid="stApp"] details > summary,
[data-testid="stApp"] details[open] > summary,
[data-testid="stApp"] details > summary:hover {{
  background:var(--pt-paper); color:var(--pt-ink);
}}
[class*="st-key-number-card-"] {{min-height:12.6rem;}}

[data-testid="stMetricValue"] {{color:var(--pt-ink);}}
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stVerticalBlock"][style*="border"] {{
  border-color:var(--pt-line); background:var(--pt-paper);
}}
[data-testid="stApp"] :is(input,button,[role="combobox"],details) {{
  background-color:var(--pt-paper); color:var(--pt-ink); border-color:var(--pt-line);
}}
[data-testid="stApp"] [role="listbox"], [data-baseweb="popover"] {{color:var(--pt-ink);}}
[data-testid="stMainBlockContainer"] {{max-width:1250px; padding-top:3.1rem; padding-bottom:4rem;}}
[data-testid="stApp"] {{font-variant-numeric:tabular-nums;}}
h1 {{letter-spacing:-.045em;}}
h2 {{letter-spacing:-.025em;}}
.eyebrow {{display:block; margin-top:1.1rem; color:var(--pt-accent); font-weight:750;
  text-transform:uppercase; letter-spacing:.13em; font-size:.71rem;}}
.header-note {{color:var(--pt-muted); font-size:.94rem; letter-spacing:.01em;}}
.bottom-summary {{font-size:1.08rem; line-height:1.55;}}
.original-inputs {{padding:.8rem; background:var(--pt-soft); border:1px solid var(--pt-line);
  border-radius:.6rem; margin:.3rem 0; font-size:.85rem; line-height:1.55;}}
.changed-case {{padding:.85rem 1rem; background:var(--pt-soft); color:var(--pt-ink);
  border-left:4px solid var(--pt-accent); border-radius:.35rem;}}
.report-table {{overflow-x:auto; width:100%; margin:.35rem 0 .65rem;}}
.report-table table {{width:100%; border:1px solid var(--pt-line); border-collapse:collapse;
  color:var(--pt-ink); font-size:.88rem;}}
.report-table :is(th,td) {{border-bottom:1px solid var(--pt-line); padding:.63rem .7rem;
  text-align:left; vertical-align:top;}}
.report-table th {{background:var(--pt-soft); font-weight:700; white-space:nowrap;}}
.report-table td {{background:var(--pt-paper);}}
.report-table .pass, .status-pass {{background:var(--pt-pass-bg); color:var(--pt-pass);}}
.report-table .fail, .status-fail {{background:var(--pt-fail-bg); color:var(--pt-fail);}}
.report-table .over, .status-over {{background:var(--pt-caution-bg); color:var(--pt-caution);}}
.report-table .none, .status-none {{background:var(--pt-soft); color:var(--pt-muted);}}
.report-table .base {{box-shadow:inset 0 0 0 2px var(--pt-accent); font-weight:750;}}
.placeholder {{display:inline-block; border:1px dashed var(--pt-accent);
  background:var(--pt-soft); color:var(--pt-accent); padding:.22rem .42rem; border-radius:.25rem;
  font-size:.76rem; font-weight:700; white-space:nowrap;}}
.fund-dot {{display:inline-block;width:.68rem;height:.68rem;border-radius:50%;margin-right:.42rem;}}
.flow {{display:flex;flex-wrap:wrap; gap:.45rem; align-items:center;margin:.5rem 0 1rem;}}
.flow span {{background:var(--pt-soft); border:1px solid var(--pt-line); border-radius:.4rem;
  padding:.4rem .58rem; font-size:.83rem; color:var(--pt-ink);}}
.flow b {{color:var(--pt-accent);}}
.legend-chip {{display:inline-block; padding:.2rem .45rem; border-radius:.25rem;
  margin-right:.5rem; font-size:.8rem;}}
.legend-chip.base {{box-shadow:inset 0 0 0 1px var(--pt-accent);}}
.decision-fields {{display:grid;grid-template-columns:minmax(9rem, .35fr) 1fr;gap:.65rem;align-items:center;}}
@media(max-width:700px) {{
  [data-testid="stMainBlockContainer"] {{padding:2rem 1rem;}}
  .decision-fields {{grid-template-columns:1fr;}}
}}
</style>""")


def chart_style(fig, dark, height):
    ink = '#e8effb' if dark else '#172c4b'
    fig.update_layout(template='plotly_dark' if dark else 'plotly_white',
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font={'family': 'Source Sans, Source Sans Pro, sans-serif', 'color': ink},
                      height=height, margin={'l': 18, 'r': 18, 't': 30, 'b': 30})
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


def allocation_chart(candidate, names, size, dark):
    positive = [(ticker, weight) for ticker, weight in zip(names, candidate['weights']) if weight > 0]
    labels = [f'{ticker} {percent(weight)}' for ticker, weight in positive]
    fig = go.Figure(go.Pie(
        labels=labels, values=[weight for _, weight in positive],
        customdata=[[FUNDS[ticker][0], dollars(weight * size)] for ticker, weight in positive],
        marker={'colors': [FUNDS[ticker][2] for ticker, _ in positive]}, hole=.55,
        sort=False, textinfo='label', textposition='outside', automargin=True,
        hovertemplate='%{label}<br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>',
        showlegend=False))
    fig.add_annotation(text=f'<b>{dollars(size)}</b>', x=.5, y=.5, showarrow=False, font={'size': 19})
    return chart_style(fig, dark, 340)


@st.cache_data(show_spinner=False)
def tested_mixes(vehicles, correlations, caps, annual_cost):
    covariance = portfolio.covariance_matrix(vehicles, correlations)
    reserve_index = next(i for i, asset in enumerate(vehicles) if asset[0] == 'SGOV')
    return [(portfolio.portfolio_volatility(weights, covariance),
             portfolio.expected_return(weights, vehicles) - annual_cost,
             weights[reserve_index])
            for weights in portfolio.grid_allocations(len(vehicles), caps)]


def frontier_chart(points, candidate, settings, dark):
    fig = go.Figure()
    fig.add_scatter(x=[point[0] for point in points], y=[point[1] for point in points],
                    mode='markers', name='Tested mixes',
                    marker={'size': 4, 'color': '#6896c4' if dark else '#779bc4', 'opacity': .4},
                    hovertemplate='Volatility %{x:.1%}<br>Annual return %{y:.1%}<extra></extra>')
    boundary = []
    highest = float('-inf')
    for risk, gain, reserve in sorted(points, key=lambda point: (point[0], -point[1])):
        if reserve + 1e-12 >= settings.reserve and gain > highest + 1e-12:
            boundary.append((risk, gain))
            highest = gain
    if boundary:
        fig.add_scatter(x=[point[0] for point in boundary], y=[point[1] for point in boundary],
                        mode='lines', name='Efficient frontier', line={'color': '#397fc0', 'width': 2})
    if candidate:
        fig.add_scatter(x=[candidate['volatility']], y=[candidate['net_return_proxy']],
                        mode='markers', name='Selected mix',
                        marker={'color': '#dc995a', 'symbol': 'diamond', 'size': 13,
                                'line': {'color': '#172c4b', 'width': 1}},
                        hovertemplate='Selected mix<br>Volatility %{x:.1%}<br>Annual return %{y:.1%}<extra></extra>')
    line = '#a9bdd8' if dark else '#597390'
    fig.add_hline(y=settings.target, line={'dash': 'dot', 'color': line})
    fig.add_vline(x=settings.volatility_limit, line={'dash': 'dash', 'color': line})
    fig.add_scatter(x=[None], y=[None], mode='lines', name='Return target',
                    line={'dash': 'dot', 'color': line})
    fig.add_scatter(x=[None], y=[None], mode='lines', name='Volatility limit',
                    line={'dash': 'dash', 'color': line})
    fig.update_xaxes(title='Annual Volatility (%)', tickformat='.1%', rangemode='nonnegative')
    fig.update_yaxes(title='Expected Annual Return (%)', tickformat='.1%')
    fig.update_layout(legend={'orientation': 'h', 'y': 1.13, 'x': 0})
    return chart_style(fig, dark, 440)


def grid_results(points, reserve):
    eligible = [(risk, gain) for risk, gain, cash in points if cash + 1e-12 >= reserve]
    return [min((risk for risk, gain in eligible if gain + 1e-12 >= goal), default=None)
            for goal in GOALS]
