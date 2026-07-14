"""
Interactive Yen's K-Shortest Paths explainer using matplotlib.

Usage:
    python3 yen_explainer.py <map_file>

Controls:
    RIGHT / SPACE  - next step
    LEFT           - previous step
    Q / ESC        - quit
"""

import sys
import heapq
import textwrap
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

import matplotlib
matplotlib.use("TkAgg")  # works headlessly if needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D

# ── re-use your project's models and parser ──────────────────────────────────
sys.path.insert(0, ".")
from models import Hub, Sim, ZONE_COST
from parser import parse


# ─────────────────────────────────────────────────────────────────────────────
# Minimal Dijkstra (same logic as dijkstra.py but self-contained)
# ─────────────────────────────────────────────────────────────────────────────

def _dijkstra(
    sim: Sim,
    start: Hub,
    end: Hub,
    removed: FrozenSet[Tuple[str, str]] = frozenset(),
) -> Optional[List[Hub]]:
    dist: Dict[str, float] = {n: float("inf") for n in sim.hubs}
    prev: Dict[str, Optional[str]] = {n: None for n in sim.hubs}
    dist[start.name] = 0.0
    heap: List[Tuple[float, int, str]] = [(0.0, 0, start.name)]
    visited: Set[str] = set()
    ctr = 0

    while heap:
        cost, _, name = heapq.heappop(heap)
        if name in visited:
            continue
        visited.add(name)
        if name == end.name:
            break
        for nb, _ in sim.neighbors(sim.hubs[name]):
            if nb.zone == "blocked":
                continue
            if (name, nb.name) in removed or (nb.name, name) in removed:
                continue
            nc = cost + float(ZONE_COST.get(nb.zone, 999))
            if nc < dist[nb.name]:
                dist[nb.name] = nc
                prev[nb.name] = name
                ctr += 1
                heapq.heappush(heap, (nc, ctr, nb.name))

    if dist[end.name] == float("inf"):
        return None
    names: List[str] = []
    cur: Optional[str] = end.name
    while cur:
        names.insert(0, cur)
        cur = prev[cur]
    return [sim.hubs[n] for n in names] if names[0] == start.name else None


def _path_cost(path: List[Hub]) -> float:
    return sum(float(ZONE_COST.get(h.zone, 1)) for h in path[1:])


# ─────────────────────────────────────────────────────────────────────────────
# Build all steps Yen's algorithm takes, recording what happened each step
# ─────────────────────────────────────────────────────────────────────────────

class Step:
    """One frame in the explainer animation."""
    def __init__(
        self,
        title: str,
        description: str,
        confirmed_paths: List[List[Hub]],
        highlight_path: Optional[List[Hub]] = None,
        highlight_color: str = "gold",
        removed_edges: Optional[Set[Tuple[str, str]]] = None,
        spur_node: Optional[Hub] = None,
        root_path: Optional[List[Hub]] = None,
        candidates: Optional[List[List[Hub]]] = None,
    ) -> None:
        self.title = title
        self.description = description
        self.confirmed_paths = confirmed_paths          # green paths
        self.highlight_path = highlight_path            # path being examined
        self.highlight_color = highlight_color
        self.removed_edges = removed_edges or set()     # red blocked edges
        self.spur_node = spur_node                      # orange dot
        self.root_path = root_path or []                # blue prefix
        self.candidates = candidates or []              # grey dashed candidates


def build_steps(sim: Sim, start: Hub, end: Hub, k: int) -> List[Step]:
    steps: List[Step] = []

    # ── Step 0: show the bare graph ──────────────────────────────────────────
    steps.append(Step(
        title="The Graph",
        description=(
            "This is your map. Every circle is a hub, every line is a connection.\n"
            f"We want to find the {k} shortest paths from '{start.name}' to '{end.name}'.\n"
            "Green = start/end.  Zone costs: normal=1, priority=1, restricted=2."
        ),
        confirmed_paths=[],
    ))

    # ── Step 1: run first Dijkstra ────────────────────────────────────────────
    first = _dijkstra(sim, start, end)
    if first is None:
        return steps

    steps.append(Step(
        title="Step 1 — Run Dijkstra",
        description=(
            "Plain Dijkstra finds the single cheapest path.\n"
            f"Path #1: {' → '.join(h.name for h in first)}\n"
            f"Cost: {_path_cost(first):.0f} turns."
        ),
        confirmed_paths=[],
        highlight_path=first,
        highlight_color="limegreen",
    ))

    steps.append(Step(
        title="Path #1 Confirmed",
        description=(
            f"Path #1 is confirmed as our first result.\n"
            f"{' → '.join(h.name for h in first)}  (cost {_path_cost(first):.0f})\n\n"
            "Now we run Yen's algorithm to find alternatives."
        ),
        confirmed_paths=[first],
    ))

    # ── Yen's outer loop ──────────────────────────────────────────────────────
    paths: List[List[Hub]] = [first]
    candidates: List[Tuple[float, int, List[Hub]]] = []
    seen: Set[Tuple[str, ...]] = {tuple(h.name for h in first)}
    tie = 0
    all_candidate_paths: List[List[Hub]] = []

    for i in range(1, k):
        prev_path = paths[i - 1]

        steps.append(Step(
            title=f"Finding Path #{i + 1} — Walk Along Path #{i}",
            description=(
                f"To find path #{i+1}, we walk along path #{i} hub by hub.\n"
                f"At each hub we ask: 'what if we took a different turn here?'\n"
                f"Path #{i}: {' → '.join(h.name for h in prev_path)}"
            ),
            confirmed_paths=list(paths),
            highlight_path=prev_path,
            highlight_color="deepskyblue",
        ))

        for spur_idx in range(len(prev_path) - 1):
            spur_node = prev_path[spur_idx]
            root_path = prev_path[:spur_idx]

            # collect edges to block
            removed: Set[Tuple[str, str]] = set()
            for p in paths:
                if p[:spur_idx] == root_path:
                    removed.add((p[spur_idx].name, p[spur_idx + 1].name))

            for hub in root_path:
                for nb, _ in sim.neighbors(hub):
                    removed.add((hub.name, nb.name))
                    removed.add((nb.name, hub.name))

            steps.append(Step(
                title=f"Path #{i+1} — Spur at '{spur_node.name}'",
                description=(
                    f"Branch-off point (spur): '{spur_node.name}'\n"
                    f"Prefix kept (root):  {' → '.join(h.name for h in root_path) or '(none)'}\n\n"
                    f"RED edges are blocked:\n"
                    f"  • edges known paths used at this spur point\n"
                    f"  • all edges touching root nodes (prevents loops)\n\n"
                    "Now run Dijkstra from the spur with those edges removed."
                ),
                confirmed_paths=list(paths),
                highlight_path=prev_path,
                highlight_color="deepskyblue",
                removed_edges=set(removed),
                spur_node=spur_node,
                root_path=list(root_path),
                candidates=list(all_candidate_paths),
            ))

            spur_path = _dijkstra(sim, spur_node, end, frozenset(removed))

            if spur_path is None:
                steps.append(Step(
                    title=f"Spur at '{spur_node.name}' — Dead End",
                    description=(
                        f"Dijkstra from '{spur_node.name}' with blocked edges\n"
                        "found NO path to the end. Skipping this spur point."
                    ),
                    confirmed_paths=list(paths),
                    removed_edges=set(removed),
                    spur_node=spur_node,
                    root_path=list(root_path),
                    candidates=list(all_candidate_paths),
                ))
                continue

            full_path = root_path + spur_path
            key = tuple(h.name for h in full_path)

            if key in seen:
                steps.append(Step(
                    title=f"Spur at '{spur_node.name}' — Duplicate",
                    description=(
                        f"Found: {' → '.join(h.name for h in full_path)}\n"
                        "But this path was already found before — skip it."
                    ),
                    confirmed_paths=list(paths),
                    highlight_path=full_path,
                    highlight_color="grey",
                    removed_edges=set(removed),
                    spur_node=spur_node,
                    root_path=list(root_path),
                    candidates=list(all_candidate_paths),
                ))
                continue

            seen.add(key)
            cost = _path_cost(full_path)
            tie += 1
            heapq.heappush(candidates, (cost, tie, full_path))
            all_candidate_paths.append(full_path)

            steps.append(Step(
                title=f"Spur at '{spur_node.name}' — New Candidate Found",
                description=(
                    f"New candidate path discovered:\n"
                    f"{' → '.join(h.name for h in full_path)}\n"
                    f"Cost: {cost:.0f}  → added to the candidates heap."
                ),
                confirmed_paths=list(paths),
                highlight_path=full_path,
                highlight_color="orange",
                removed_edges=set(removed),
                spur_node=spur_node,
                root_path=list(root_path),
                candidates=list(all_candidate_paths),
            ))

        if not candidates:
            steps.append(Step(
                title="No More Paths",
                description=(
                    "The candidates heap is empty — no more alternative\n"
                    f"routes exist in this graph. Stopping at {len(paths)} path(s)."
                ),
                confirmed_paths=list(paths),
            ))
            break

        _, _, best = heapq.heappop(candidates)
        # remove from display list too
        if best in all_candidate_paths:
            all_candidate_paths.remove(best)
        paths.append(best)

        steps.append(Step(
            title=f"Path #{i + 1} Confirmed",
            description=(
                f"Pop the cheapest candidate from the heap:\n"
                f"Path #{i+1}: {' → '.join(h.name for h in best)}\n"
                f"Cost: {_path_cost(best):.0f} turns.\n\n"
                f"Remaining candidates: {len(candidates)}"
            ),
            confirmed_paths=list(paths),
            highlight_path=best,
            highlight_color="limegreen",
            candidates=list(all_candidate_paths),
        ))

    # ── Final summary ─────────────────────────────────────────────────────────
    steps.append(Step(
        title=f"Done — {len(paths)} Paths Found",
        description=(
            "All paths discovered by Yen's algorithm:\n\n" +
            "\n".join(
                f"  #{j+1} (cost {_path_cost(p):.0f}): "
                f"{' → '.join(h.name for h in p)}"
                for j, p in enumerate(paths)
            )
        ),
        confirmed_paths=list(paths),
    ))

    return steps


# ─────────────────────────────────────────────────────────────────────────────
# Drawing
# ─────────────────────────────────────────────────────────────────────────────

# Distinct colours for each confirmed path
PATH_COLORS = [
    "limegreen", "deepskyblue", "violet", "orange",
    "hotpink", "aquamarine", "gold", "tomato",
]

ZONE_NODE_COLORS = {
    "normal":     "#4a90d9",
    "priority":   "#f5c242",
    "restricted": "#e06c6c",
    "blocked":    "#555555",
}


def _hub_pos(hub: Hub) -> Tuple[float, float]:
    return float(hub.x), float(hub.y)


def draw_step(ax: plt.Axes, sim: Sim, step: Step, start: Hub, end: Hub) -> None:
    ax.clear()
    ax.set_aspect("equal")
    ax.set_facecolor("#1a1a2e")
    ax.axis("off")

    hubs = list(sim.hubs.values())
    pos = {h.name: _hub_pos(h) for h in hubs}

    # ── collect which edges belong to which confirmed path ────────────────────
    confirmed_edge_colors: Dict[Tuple[str, str], str] = {}
    for pidx, path in enumerate(step.confirmed_paths):
        color = PATH_COLORS[pidx % len(PATH_COLORS)]
        for a, b in zip(path, path[1:]):
            confirmed_edge_colors[(a.name, b.name)] = color
            confirmed_edge_colors[(b.name, a.name)] = color

    # ── draw all connections ──────────────────────────────────────────────────
    drawn_conns: Set[frozenset] = set()
    for conn in sim.connections.values():
        key = frozenset({conn.hub_a, conn.hub_b})
        if key in drawn_conns:
            continue
        drawn_conns.add(key)

        x1, y1 = pos[conn.hub_a]
        x2, y2 = pos[conn.hub_b]
        edge = (conn.hub_a, conn.hub_b)
        rev  = (conn.hub_b, conn.hub_a)

        is_removed = edge in step.removed_edges or rev in step.removed_edges

        if is_removed:
            ax.plot([x1, x2], [y1, y2], color="red", lw=2.5,
                    linestyle="--", alpha=0.85, zorder=1)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my, "✖", color="red", fontsize=9,
                    ha="center", va="center", zorder=5)
        elif edge in confirmed_edge_colors:
            ax.plot([x1, x2], [y1, y2],
                    color=confirmed_edge_colors[edge], lw=3,
                    alpha=0.9, zorder=2)
        else:
            ax.plot([x1, x2], [y1, y2],
                    color="#444466", lw=1.5, alpha=0.6, zorder=1)

    # ── draw candidate paths (dashed grey) ───────────────────────────────────
    for cpath in step.candidates:
        for a, b in zip(cpath, cpath[1:]):
            x1, y1 = pos[a.name]
            x2, y2 = pos[b.name]
            ax.plot([x1, x2], [y1, y2],
                    color="grey", lw=1.5, linestyle=":",
                    alpha=0.5, zorder=2)

    # ── draw highlighted path ─────────────────────────────────────────────────
    if step.highlight_path:
        for a, b in zip(step.highlight_path, step.highlight_path[1:]):
            x1, y1 = pos[a.name]
            x2, y2 = pos[b.name]
            ax.plot([x1, x2], [y1, y2],
                    color=step.highlight_color, lw=4,
                    alpha=0.95, zorder=3)

    # ── draw root path (thick blue underline) ────────────────────────────────
    if step.root_path:
        for a, b in zip(step.root_path, step.root_path[1:]):
            x1, y1 = pos[a.name]
            x2, y2 = pos[b.name]
            ax.plot([x1, x2], [y1, y2],
                    color="royalblue", lw=6,
                    alpha=0.5, zorder=2)

    # ── draw all hub nodes ────────────────────────────────────────────────────
    for hub in hubs:
        x, y = pos[hub.name]
        node_color = ZONE_NODE_COLORS.get(hub.zone, "#888888")

        # special colours for start / end
        if hub.name == start.name:
            node_color = "limegreen"
        elif hub.name == end.name:
            node_color = "gold"

        # root path nodes get a blue ring
        in_root = hub in (step.root_path or [])
        ring_color = "royalblue" if in_root else "white"
        ring_lw = 3 if in_root else 1

        circle = plt.Circle((x, y), 0.3, color=node_color,
                             ec=ring_color, lw=ring_lw, zorder=6)
        ax.add_patch(circle)
        ax.text(x, y - 0.5, hub.name, color="white",
                fontsize=7, ha="center", va="top",
                fontweight="bold", zorder=7)

        # cost label inside node
        cost_str = str(ZONE_COST.get(hub.zone, "?"))
        ax.text(x, y, cost_str, color="black",
                fontsize=7, ha="center", va="center",
                fontweight="bold", zorder=8)

    # ── spur node highlight ───────────────────────────────────────────────────
    if step.spur_node:
        sx, sy = pos[step.spur_node.name]
        ring = plt.Circle((sx, sy), 0.42, color="none",
                           ec="orange", lw=3, zorder=9)
        ax.add_patch(ring)
        ax.text(sx, sy + 0.6, "spur", color="orange",
                fontsize=7, ha="center", va="bottom",
                fontweight="bold", zorder=10)

    # ── legend ────────────────────────────────────────────────────────────────
    legend_elements = [
        Line2D([0], [0], color="limegreen", lw=2, label="confirmed path"),
        Line2D([0], [0], color="orange", lw=2, label="new candidate"),
        Line2D([0], [0], color="deepskyblue", lw=2, label="path being examined"),
        Line2D([0], [0], color="royalblue", lw=4,
               alpha=0.5, label="root prefix (kept)"),
        Line2D([0], [0], color="red", lw=2,
               linestyle="--", label="blocked edge"),
        Line2D([0], [0], color="grey", lw=1.5,
               linestyle=":", label="candidate (heap)"),
        mpatches.Patch(color="limegreen", label="start / confirmed"),
        mpatches.Patch(color="gold", label="end / goal"),
        mpatches.Patch(color=ZONE_NODE_COLORS["restricted"], label="restricted (cost 2)"),
        mpatches.Patch(color=ZONE_NODE_COLORS["priority"], label="priority (cost 1)"),
    ]
    ax.legend(
        handles=legend_elements,
        loc="upper left",
        fontsize=7,
        facecolor="#1a1a2e",
        edgecolor="#444466",
        labelcolor="white",
        framealpha=0.85,
    )


def draw_description(ax: plt.Axes, step: Step, idx: int, total: int) -> None:
    ax.clear()
    ax.set_facecolor("#12122a")
    ax.axis("off")

    ax.text(
        0.5, 0.97, step.title,
        transform=ax.transAxes,
        color="#f0c040", fontsize=13, fontweight="bold",
        ha="center", va="top",
    )

    wrapped = textwrap.fill(step.description, width=55)
    ax.text(
        0.5, 0.75, wrapped,
        transform=ax.transAxes,
        color="#ccccee", fontsize=9,
        ha="center", va="top",
        family="monospace",
        linespacing=1.6,
    )

    ax.text(
        0.5, 0.08,
        f"Step {idx + 1} / {total}   ◄ LEFT  |  RIGHT ►  |  Q to quit",
        transform=ax.transAxes,
        color="#667799", fontsize=8,
        ha="center", va="bottom",
    )

    # progress bar
    bar_w = 0.8
    bar_x = (1 - bar_w) / 2
    ax.add_patch(mpatches.FancyBboxPatch(
        (bar_x, 0.03), bar_w, 0.03,
        boxstyle="round,pad=0.005",
        facecolor="#2a2a4a", edgecolor="#444466",
        transform=ax.transAxes, clip_on=False,
    ))
    fill = bar_w * (idx + 1) / total
    ax.add_patch(mpatches.FancyBboxPatch(
        (bar_x, 0.03), fill, 0.03,
        boxstyle="round,pad=0.005",
        facecolor="#f0c040", edgecolor="none",
        transform=ax.transAxes, clip_on=False,
    ))


# ─────────────────────────────────────────────────────────────────────────────
# Main interactive loop
# ─────────────────────────────────────────────────────────────────────────────

def run_explainer(sim: Sim, start: Hub, end: Hub, k: int = 4) -> None:
    steps = build_steps(sim, start, end, k)
    idx = [0]

    fig = plt.figure(figsize=(14, 7), facecolor="#12122a")
    fig.suptitle(
        "Yen's K-Shortest Paths — Step-by-Step Explainer",
        color="#f0c040", fontsize=14, fontweight="bold", y=0.99,
    )

    ax_graph = fig.add_axes([0.02, 0.04, 0.62, 0.92])
    ax_text  = fig.add_axes([0.66, 0.04, 0.32, 0.92])

    def redraw() -> None:
        step = steps[idx[0]]
        draw_step(ax_graph, sim, step, start, end)
        draw_description(ax_text, step, idx[0], len(steps))
        fig.canvas.draw_idle()

    def on_key(event: matplotlib.backend_bases.KeyEvent) -> None:
        if event.key in ("right", " "):
            idx[0] = min(idx[0] + 1, len(steps) - 1)
        elif event.key == "left":
            idx[0] = max(idx[0] - 1, 0)
        elif event.key in ("q", "escape"):
            plt.close(fig)
            return
        redraw()

    fig.canvas.mpl_connect("key_press_event", on_key)
    redraw()
    plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 yen_explainer.py <map_file> [k]")
        print("  map_file : path to your .txt map")
        print("  k        : number of paths to find (default 4)")
        sys.exit(1)

    info = parse(sys.argv[1])
    if info is None:
        print("Failed to parse map.")
        sys.exit(1)

    k = int(sys.argv[2]) if len(sys.argv) >= 3 else 4
    sim = Sim(info)
    run_explainer(sim, sim.start, sim.end, k)


if __name__ == "__main__":
    main()
