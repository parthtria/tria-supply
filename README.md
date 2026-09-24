# TRIA supply API

Live total and circulating supply for TRIA (Ethereum `0x228bec415ade4b61d7caf0adf8c91eac587ba369`), refreshed every 30 minutes by GitHub Actions from free public RPCs and served by GitHub Pages.

| Endpoint | Returns |
|---|---|
| `https://supply.tria.so/total.json` | total supply, whole number |
| `https://supply.tria.so/circulating.json` | circulating supply, whole number |
| `https://supply.tria.so/supply.json` | breakdown per reserve wallet + timestamp |

Circulating = total supply − balances of the reserve wallets in `wallets.json` (Magna vesting contracts and Tria treasury Safes), following CoinMarketCap's definition. No decimals, no API keys.

To change a reserve wallet, edit `wallets.json`; the next run picks it up.
