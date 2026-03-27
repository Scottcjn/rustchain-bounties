# Creator Analytics Dashboard

Flask Blueprint implementing [bottube#423](https://github.com/Scottcjn/bottube/issues/423).

## Endpoints

| Route | Description |
|-------|-------------|
| `GET /api/analytics/views?period=7d\|30d\|90d` | Daily view counts |
| `GET /api/analytics/top?sort=views\|engagement\|tips` | Top videos ranked |
| `GET /api/analytics/audience` | Human vs AI viewer ratio |
| `GET /api/analytics/export.csv` | CSV export with formula-injection protection |
| `GET /creator/analytics` | Dashboard page with Chart.js charts |

## Integration

```python
from analytics_blueprint import analytics_bp
app.register_blueprint(analytics_bp)
```

Requires `g.user`, `get_db()` from bottube_server.py. Templates extend `base.html`.

## Tests

```bash
cd creator-analytics && pip install flask && python -m pytest test_creator_analytics.py -v
```

Bounty: [rustchain-bounties#2157](https://github.com/Scottcjn/rustchain-bounties/issues/2157)
