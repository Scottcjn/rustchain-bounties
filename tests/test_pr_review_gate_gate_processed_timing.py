import scripts.pr_review_gate as gate


def _reset(monkeypatch):
    monkeypatch.setattr(gate, 'NUM', '16710')
    monkeypatch.setattr(gate, 'REPO', 'Scottcjn/rustchain-bounties')
    monkeypatch.setattr(gate, 'TARGET', 'Scottcjn/Rustchain')
    monkeypatch.setattr(gate, 'CAP', 15)
    monkeypatch.setattr(gate, 'RATE', '3')


def test_gate_processed_not_written_before_success(monkeypatch):
    _reset(monkeypatch)
    calls = []

    issue = {
        'state': 'open',
        'title': 'PR Review RustChain #9999',
        'body': 'RTC14241718572ec3bd1c0c4ee26ed2fc4bf6fca15',
        'user': {'login': 'reviewer'},
        'labels': [],
    }

    def fake_api(path, method='GET', data=None, strict=False):
        calls.append((method, path, data, strict))
        if path == '/repos/Scottcjn/rustchain-bounties/issues/16710':
            return issue
        if path == '/repos/Scottcjn/Rustchain/pulls/9999/reviews':
            raise RuntimeError('transient github 502')
        raise AssertionError(path)

    monkeypatch.setattr(gate, 'api', fake_api)
    monkeypatch.setattr(gate, 'comment', lambda *a, **k: calls.append(('COMMENT', a, k)))
    monkeypatch.setattr(gate, 'close', lambda *a, **k: calls.append(('CLOSE', a, k)))
    monkeypatch.setattr(gate, 'add_label', lambda *a, **k: calls.append(('LABEL', a, k)))

    try:
        gate.main()
    except RuntimeError:
        pass

    labels = [c for c in calls if c[0] == 'LABEL']
    assert labels == [], labels


def test_gate_processed_written_after_eligible_verdict(monkeypatch):
    _reset(monkeypatch)
    calls = []

    issue = {
        'state': 'open',
        'title': 'PR Review RustChain #9999',
        'body': 'RTC14241718572ec3bd1c0c4ee26ed2fc4bf6fca15',
        'user': {'login': 'reviewer'},
        'labels': [],
    }
    reviews = [
        {'submitted_at': '2026-08-30T12:00:00Z', 'user': {'login': 'reviewer'}, 'body': 'Ref: `src/main.py` line 44 can fail closed if the lookup times out.'}
    ]
    inline_comments = [
        {'user': {'login': 'reviewer'}}
    ]
    elig = {'total_count': 0}

    def fake_api(path, method='GET', data=None, strict=False):
        calls.append((method, path, data, strict))
        if path == '/repos/Scottcjn/rustchain-bounties/issues/16710':
            return issue
        if path == '/repos/Scottcjn/Rustchain/pulls/9999/reviews':
            return reviews
        if path == '/repos/Scottcjn/Rustchain/pulls/9999/comments?per_page=100':
            return inline_comments
        if path.startswith('/search/issues?q=user:Scottcjn+label:bounty-eligible+author:reviewer+type:issue'):
            return elig
        raise AssertionError(path)

    monkeypatch.setattr(gate, 'api', fake_api)
    monkeypatch.setattr(gate, 'comment', lambda *a, **k: calls.append(('COMMENT', a, k)))
    monkeypatch.setattr(gate, 'close', lambda *a, **k: calls.append(('CLOSE', a, k)))
    monkeypatch.setattr(gate, 'add_label', lambda *a, **k: calls.append(('LABEL', a, k)))

    gate.main()

    labels = [c[1][1] for c in calls if c[0] == 'LABEL']
    assert labels == ['bounty-eligible', 'gate-processed'], labels
