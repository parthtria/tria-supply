"""Compute TRIA total and circulating supply from on-chain balances.

Circulating = totalSupply() - sum(balanceOf(reserve wallet)) for the wallets
in wallets.json, i.e. the CoinMarketCap definition (total minus reserve
wallets). Writes plain whole-number files that CMC / exchanges can poll.
Standard library only; tries each free public RPC in turn.
"""
import json, sys, time, urllib.request
from datetime import datetime, timezone

cfg = json.load(open("wallets.json"))
TOKEN = cfg["token"]
DEC = 10 ** cfg["decimals"]
SEL_TOTAL = "0x18160ddd"          # totalSupply()
SEL_BAL = "0x70a08231"            # balanceOf(address)


def rpc(url, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "tria-supply/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(out["error"])
    return int(out["result"], 16)


def call(url, data):
    return rpc(url, "eth_call", [{"to": TOKEN, "data": data}, "latest"])


def fetch(url):
    total = call(url, SEL_TOTAL)
    balances = {}
    for name, addr in cfg["reserve_wallets"].items():
        balances[name] = call(url, SEL_BAL + addr[2:].lower().rjust(64, "0"))
    return total, balances


last_err = None
for url in cfg["rpc_endpoints"]:
    try:
        total_raw, bal_raw = fetch(url)
        break
    except Exception as e:  # try the next endpoint
        last_err = e
        print(f"{url}: {e}", file=sys.stderr)
        time.sleep(1)
else:
    sys.exit(f"all RPC endpoints failed: {last_err}")

total = total_raw // DEC
reserve = sum(bal_raw.values()) // DEC
circulating = total - reserve

open("total.json", "w").write(str(total))
open("circulating.json", "w").write(str(circulating))
json.dump(
    {
        "total_supply": total,
        "circulating_supply": circulating,
        "reserve_total": reserve,
        "reserve_wallets": {k: v // DEC for k, v in bal_raw.items()},
        "rpc": url,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    },
    open("supply.json", "w"),
    indent=2,
)
print(f"total={total} reserve={reserve} circulating={circulating} via {url}")
