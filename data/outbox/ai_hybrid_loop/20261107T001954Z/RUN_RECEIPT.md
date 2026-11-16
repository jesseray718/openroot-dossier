# AI HYBRID LOOP v2 — 20261107T001954Z (Newton+PoPW fused)
- host: optiplex3060
- root: /home/jesse/openroot
- models: qwen2.5-coder:0.5b smollm2:1.7b qwen2.5:1.5b
- pods dir: /home/jesse/pods
- fulltext state: /home/jesse/.local/state/openroot-fulltext-v2

{
  "id": "popw-1794010802575",
  "ts": "2026-11-07T00:20:02.575090+00:00",
  "type": "thermal_cycle",
  "prev": "b771918a3275d8580a199417322c94868adea51a6464af04c59d82e169e244fc",
  "payload": {
    "cycle_id": "20261107T001954Z",
    "models": [
      "qwen2.5-coder:0.5b",
      "smollm2:1.7b",
      "qwen2.5:1.5b"
    ],
    "recall_hits": 1,
    "questions": 3,
    "eta": 1.111111,
    "human_joules": 0.9,
    "useful_joules": 1.0,
    "evidence": [
      "data/outbox/ai_hybrid_loop/20261107T001954Z/travel.json"
    ],
    "newton_tip": null,
    "pod_root": "/home/jesse/pods",
    "db_used": "/home/jesse/.local/state/openroot-fulltext-v2/knowledge.pod.sqlite3"
  },
  "hash": "e3137fafd55ea53ff8774347460f6d68d54174130beedb54d8c7d4e8fd27537c"
}
