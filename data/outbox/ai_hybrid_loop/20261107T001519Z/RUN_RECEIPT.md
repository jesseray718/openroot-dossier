# AI HYBRID LOOP v2 — 20261107T001519Z (Newton+PoPW fused)
- host: optiplex3060
- root: /home/jesse/openroot
- models: qwen2.5-coder:0.5b smollm2:1.7b qwen2.5:1.5b
- pods dir: /home/jesse/pods
- fulltext state: /home/jesse/.local/state/openroot-fulltext-v2

{
  "id": "popw-1794010572002",
  "ts": "2026-11-07T00:16:12.002723+00:00",
  "type": "thermal_cycle",
  "prev": "f40cf959d4d03126c8f889c7c8b71077eb568c83000a876f195e32b07b33da08",
  "payload": {
    "cycle_id": "20261107T001519Z",
    "models": [
      "qwen2.5-coder:0.5b",
      "smollm2:1.7b",
      "qwen2.5:1.5b"
    ],
    "recall_hits": 1,
    "questions": 1,
    "eta": 1.111111,
    "human_joules": 0.9,
    "useful_joules": 1.0,
    "evidence": [
      "data/outbox/ai_hybrid_loop/20261107T001519Z/travel.json"
    ],
    "newton_tip": null,
    "pod_root": "/home/jesse/pods",
    "db_used": "/home/jesse/.local/state/openroot-fulltext-v2/knowledge.pod.sqlite3"
  },
  "hash": "b771918a3275d8580a199417322c94868adea51a6464af04c59d82e169e244fc"
}
