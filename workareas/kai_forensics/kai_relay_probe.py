#!/usr/bin/env python3
"""Non-destructive TCP/HTTP probe. 9999 is empirical only."""
import json, socket, sys, urllib.request
def tcp_probe(host, port, timeout=2.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "open"
    except OSError as e:
        return f"closed ({type(e).__name__})"
def http_probe(url, timeout=4):
    out = {}
    for method in ("GET", "OPTIONS"):
        req = urllib.request.Request(url, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out[method] = {"status": r.status, "server": r.headers.get("Server", ""),
                               "allow": r.headers.get("Allow", ""),
                               "head": r.read(256).decode(errors="replace")[:120]}
        except Exception as e:
            out[method] = f"{type(e).__name__}"
    return out
def main():
    core = sys.argv[1] if len(sys.argv) > 1 else "100.122.169.43"
    ports = [int(p) for p in (sys.argv[2] if len(sys.argv) > 2 else "9999,11434,8080,3000,8765").split(",")]
    hosts = ["127.0.0.1", core]
    report = []
    for h in hosts:
        for p in ports:
            st = tcp_probe(h, p)
            entry = {"host": h, "port": p, "tcp": st}
            print(f"{h}:{p:<6} -> {st}")
            if st == "open":
                base = f"http://{h}:{p}"
                entry["http_root"] = http_probe(base + "/")
                for path in ("/health", "/docs", "/openapi.json", "/v1/models", "/api/tags"):
                    entry[f"path{path.replace('/','_')}"] = http_probe(base + path)
                print("    OPEN — details in JSON")
            report.append(entry)
    print("---JSON---")
    print(json.dumps(report, indent=2))
if __name__ == "__main__":
    main()
