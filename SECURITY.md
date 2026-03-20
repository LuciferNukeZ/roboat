# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 2.1.x | ✅ Active |
| 2.0.x | ⚠️ Security fixes only |
| 1.x.x | ❌ End of life |

## Reporting a Vulnerability

Do not open a public GitHub issue for security vulnerabilities.

Report privately via GitHub's Security tab → **Report a vulnerability**.

We acknowledge within 48 hours and resolve confirmed issues within 7 days.

## Safe Practices

```python
import os
from roboat import RoboatClient

# Good — environment variable
client = RoboatClient(oauth_token=os.environ["ROBOAT_TOKEN"])

# Bad — hardcoded
client = RoboatClient(oauth_token="rblx_tok_abc123...")
```

Never commit `.robloxdb` files or OAuth tokens to version control.
