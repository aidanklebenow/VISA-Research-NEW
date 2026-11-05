"""Compare downloaded reports with course references; never populate production data."""
import json
from pathlib import Path
import panel

HERE = Path(__file__).resolve().parent


def main():
    cost = json.loads((HERE / 'evidence/COST-report.json').read_text())
    expected_current = [1.02, 1.07, .97, 1.03, 1.06]
    expected_leverage = [2.11, 1.75, 1.96, 1.64, 1.49]
    assert [round(r['current_ratio']['value'], 2) for r in cost['rows']] == expected_current
    assert [round(r['liabilities_equity']['value'], 2) for r in cost['rows']] == expected_leverage
    assert panel.growth_display(cost) == '7.51%'
    assert all(panel.display('rd_revenue', r['rd_revenue']) == 'not found' for r in cost['rows'])
    assert list(cost['panel']['Buffett'].values()) == ['pass'] * 3
    assert list(cost['panel']['Graham'].values()) == ['fail', 'pass', 'pass']
    assert list(cost['panel']['Burry'].values()) == ['pass'] * 2
    assert list(cost['panel']['Cathie Wood'].values()) == ['fail', 'not known']
    probe = panel.evaluate(cost, graham_current_ratio=1, wood_growth_pct=5)
    assert list(probe['Graham'].values()) == ['pass'] * 3
    assert list(probe['Cathie Wood'].values()) == ['pass', 'not known']
    evidence = {'baseline_thresholds': cost['thresholds'], 'baseline': cost['panel'],
                'probe_thresholds': {'graham_current_ratio': 1, 'wood_growth_pct': 5}, 'probe': probe,
                'data_sha256_unchanged': cost['source']['sha256'], 'student_choice': {'graham_current_ratio': 1.0, 'reason': 'Aidan chose to include Costco and use the screen as a starting point for research.'}}
    (HERE / 'evidence/threshold-probes.json').write_text(json.dumps(evidence, indent=2))
    manifest = json.loads((HERE / 'memos/manifest.json').read_text())
    for ticker in ('COST', 'NVDA', 'JPM'):
        report = json.loads((HERE / f'evidence/{ticker}-report.json').read_text())
        assert manifest[ticker]['source_sha256'] == report['source']['sha256']
        for slug in ('buffett', 'graham', 'burry', 'wood'):
            memo = (HERE / f'memos/{ticker}-{slug}.md').read_text()
            assert not panel.unsupported_numbers(memo, report), (ticker, slug, panel.unsupported_numbers(memo, report))
            assert panel.unsupported_numbers(memo + ' Unsupported 40.0%.', report) == ['40.0%']
    jpm = json.loads((HERE / 'evidence/JPM-report.json').read_text())
    assert all(r['owner_earnings']['value'] is None for r in jpm['rows'])
    assert all(r['current_ratio']['value'] is None for r in jpm['rows'])
    assert list(jpm['panel']['Graham'].values())[0] == 'not known'
    print('COST: all ratios, growth, missing R&D, and four investor screens match.')
    print('Threshold probes: Graham fails → passes; Wood growth fails → passes; R&D stays unknown.')
    print('COST/NVDA/JPM: all twelve memo checks pass; unsupported percentage flagged in each.')
    print('JPM: missing owner earnings and current ratio preserved; no zero substitution.')


if __name__ == '__main__':
    main()
