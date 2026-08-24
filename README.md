# Smart Disaster Response Platform

A backend system that coordinates disaster response — connecting **victims → rescue routing → hospital allocation** — using real graph algorithms and optimization techniques on real road-network data.

Built to explore how classic DSA (Dijkstra, A*, priority queues, the Hungarian algorithm) applies to a genuine real-world coordination problem, rather than toy examples.

## What it does

When a disaster (flood, earthquake, cyclone, landslide) hits, response is often slowed by manual, ad-hoc decision-making: which victim gets help first, what's the fastest route to reach them, and which hospital should they go to. This system automates those three decisions:

1. **Who's most urgent?** — a priority queue ranks incidents by severity and how long they've waited, so cases aren't just served first-come-first-served.
2. **What's the fastest route?** — real road-network routing (Dijkstra and A*) computed on actual OpenStreetMap data, not straight-line distance.
3. **Which hospital should they go to?** — the Hungarian algorithm finds the globally optimal victim-to-hospital assignment, which can beat a naive "nearest available" approach.

All three are wired together into a single `/dispatch` endpoint that pulls the next urgent incident, computes real routes to every hospital, and returns the best assignment — end to end.

## Why these algorithms

- **Dijkstra** — baseline shortest-path routing on the real road graph.
- **A\*** — same guarantee of correctness as Dijkstra, but guided toward the destination using a haversine-distance heuristic. Benchmarked against Dijkstra on real road networks across two Indian cities: **70–78% fewer nodes explored**, identical shortest-path distance in both cases.
- **Priority queue (max-heap)** — incidents are scored by `severity + (wait_time × urgency_weight)`. The `urgency_weight` value was tuned empirically: tested at 2, 5, and 10, with 5 chosen because it's the point where a 30-minute wait can outweigh a one-level severity difference — preventing lower-severity cases from waiting indefinitely, without letting wait time dominate over genuinely critical cases.
- **Hungarian algorithm** (`scipy.optimize.linear_sum_assignment`) — solves victim-to-hospital assignment as a bipartite matching problem, minimizing *total* travel distance across everyone. Tested against a greedy nearest-first baseline in a deliberately conflicting scenario (two victims near the same hospital): the Hungarian algorithm produced a lower total distance, since greedy lets the first-processed victim "steal" a resource a different victim needed more.

## Tested locations

Routing is tested across real, disaster-prone regions of India rather than one arbitrary city — flood-prone (Kochi, Guwahati, Patna...), cyclone-prone (Puri, Chennai...), earthquake-prone (Dehradun, Bhuj...), and landslide-prone (Wayanad, Nainital...) areas. See `algorithms/disaster_prone_locations.py` for the full list.

## Architecture

```
Client (curl / Swagger UI /docs)
        │
        ▼
FastAPI backend (backend/)
 ├── /incidents        → triage priority queue
 ├── /route             → Dijkstra / A* on real OSM road data
 ├── /allocate           → Hungarian algorithm victim-hospital matching
 └── /dispatch           → combines all three into one workflow
        │
        ▼
algorithms/ (hand-written, not just library calls)
 ├── graph.py            → Dijkstra on a toy graph (first proof of concept)
 ├── astar.py            → Dijkstra + A*, benchmarked, on real OSM data
 ├── triage.py           → priority queue with tunable urgency weighting
 ├── allocation.py       → Hungarian algorithm vs. greedy baseline
 └── disaster_prone_locations.py → curated test locations across India
```

## Tech stack

- **Backend:** Python, FastAPI, Uvicorn
- **Road network data:** OSMnx (OpenStreetMap), NetworkX
- **Optimization:** SciPy (Hungarian algorithm), scikit-learn (nearest-node search)
- **Algorithms:** hand-written Dijkstra, A*, priority queue, and cost-matrix construction — not just calling a black-box shortest-path function

## Running it locally

```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
source venv/bin/activate         # Mac/Linux

pip install -r requirements.txt

uvicorn backend.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for interactive API documentation (Swagger UI) — every endpoint can be tested directly from the browser.

## Example: full dispatch workflow

```bash
# 1. Report an incident
curl -X POST http://127.0.0.1:8000/incidents \
  -H "Content-Type: application/json" \
  -d '{"location": "Kochi Ward 3", "severity": 4, "lat": 9.9500, "lon": 76.3100}'

# 2. Dispatch the most urgent incident — finds the nearest hospital
#    using real road routing
curl -X POST "http://127.0.0.1:8000/dispatch?place_name=Kochi,%20Kerala,%20India"
```

Response includes the assigned hospital, real route distance, and the algorithm's internal stats (nodes expanded, path length).

## What's not built yet

- Shelter placement optimization (k-means clustering) — planned
- Frontend/map dashboard — currently API-only, tested via Swagger UI
- Persistent database — the triage queue is currently in-memory and resets on server restart
- Real-time updates (WebSockets) — not yet implemented

## Status

This is an active learning project — the core algorithmic engine (routing, prioritization, allocation) is built, tested, and wired into a live backend. Frontend and persistence are the next planned steps.