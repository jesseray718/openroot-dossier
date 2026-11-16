# AI HYBRID LOOP v2 — 20261107T002204Z (Newton+PoPW fused)
- host: optiplex3060
- root: /home/jesse/openroot
- models: qwen2.5-coder:0.5b smollm2:1.7b qwen2.5:1.5b
- pods dir: /home/jesse/pods
- fulltext state: /home/jesse/.local/state/openroot-fulltext-v2

{
  "id": "popw-1794010927863",
  "ts": "2026-11-07T00:22:07.863556+00:00",
  "type": "thermal_cycle",
  "prev": "e3137fafd55ea53ff8774347460f6d68d54174130beedb54d8c7d4e8fd27537c",
  "payload": {
    "cycle_id": "20261107T002204Z",
    "models": [
      "qwen2.5-coder:0.5b",
      "smollm2:1.7b",
      "qwen2.5:1.5b"
    ],
    "recall_hits": 2,
    "questions": 2,
    "eta": 1.111111,
    "human_joules": 0.9,
    "useful_joules": 1.0,
    "evidence": [
      "data/outbox/ai_hybrid_loop/20261107T002204Z/travel.json"
    ],
    "newton_tip": null,
    "pod_root": "/home/jesse/pods",
    "db_used": "/home/jesse/.local/state/openroot-fulltext-v2/knowledge.pod.sqlite3"
  },
  "hash": "ca5b357fcf52396f4bd834dd5662c93ce8d9344c76b3b227228793205d6d01a7"
}
