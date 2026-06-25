#!/usr/bin/env python3
# 把叉車在倉庫裡的行走軌跡畫成俯視圖(純 CPU、不需 render)。
# 用法:python3 scripts/plot_trajectory.py poses.txt worlds/forklift_in_warehouse.sdf out.png
#   poses.txt = `gz topic -e -t /model/forklift/pose` 的輸出
import re, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

poses_path, world_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

# --- 叉車軌跡:抓每筆 name:"forklift" 後的 position x/y ---
txt = open(poses_path, errors="ignore").read()
traj = [(float(x), float(y)) for x, y in re.findall(
    r'name:\s*"forklift"\s*(?:\n[^\n]*)*?position\s*\{\s*x:\s*(-?[\d.eE+-]+)\s*y:\s*(-?[\d.eE+-]+)',
    txt)]
# 去重連續重複點
dedup = []
for p in traj:
    if not dedup or (abs(p[0]-dedup[-1][0]) > 1e-4 or abs(p[1]-dedup[-1][1]) > 1e-4):
        dedup.append(p)
traj = dedup

# --- 倉庫障礙:每個 aws_robomaker_warehouse_* model 的名稱 + pose(取 include 後第一個 pose)---
world = open(world_path, errors="ignore").read()
obstacles = []
for m in re.finditer(r'<model name="(aws_robomaker_warehouse_[^"]+)">(.*?)</model>', world, re.S):
    name, body = m.group(1), m.group(2)
    pm = re.search(r'<pose[^>]*>\s*([-\d.eE]+)\s+([-\d.eE]+)', body)
    if pm:
        obstacles.append((name, float(pm.group(1)), float(pm.group(2))))

# 障礙類型 → 顏色/大小(近似 footprint,僅示意)
def kind(n):
    for k in ("ShelfD","ShelfE","ShelfF","WallB","GroundB","RoofB","Lamp",
              "Bucket","ClutteringA","ClutteringC","ClutteringD","DeskC","TrashCanC","PalletJackB"):
        if k in n: return k
    return "?"
SIZE = {"ShelfD":(1.0,2.6),"ShelfE":(1.0,2.6),"ShelfF":(2.6,1.0),"DeskC":(1.4,0.7),
        "Bucket":(0.4,0.4),"ClutteringA":(0.8,0.8),"ClutteringC":(0.8,0.8),
        "ClutteringD":(1.0,1.0),"TrashCanC":(0.4,0.4),"PalletJackB":(1.6,0.7)}
SKIP = {"GroundB","RoofB","Lamp","WallB"}

fig, ax = plt.subplots(figsize=(10, 8))
for name, x, y in obstacles:
    k = kind(name)
    if k in SKIP: continue
    w, h = SIZE.get(k, (0.6, 0.6))
    ax.add_patch(Rectangle((x-w/2, y-h/2), w, h, facecolor="#cfd6df",
                           edgecolor="#9aa3ad", linewidth=0.8, zorder=1))
    ax.text(x, y, k.replace("01","").replace("Cluttering","Clut"),
            fontsize=6, ha="center", va="center", color="#5b6470", zorder=2)

if traj:
    xs, ys = zip(*traj)
    ax.plot(xs, ys, "-", color="#2563eb", linewidth=2.2, zorder=5, label="forklift path")
    ax.plot(xs[0], ys[0], "o", color="#10b981", markersize=11, zorder=6, label="start")
    ax.plot(xs[-1], ys[-1], "s", color="#ef4444", markersize=11, zorder=6, label="end")
    # 行進方向箭頭
    for i in range(0, len(traj)-1, max(1, len(traj)//8)):
        dx, dy = xs[i+1]-xs[i], ys[i+1]-ys[i]
        if dx or dy:
            ax.annotate("", xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                        arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.2), zorder=5)
    ax.legend(loc="upper right", fontsize=9)

ax.set_aspect("equal")
ax.grid(True, color="#eef2f7")
ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
ax.set_title(f"Forklift driving in AWS Small Warehouse (CI, {len(traj)} pose samples)")
plt.tight_layout()
plt.savefig(out_path, dpi=110)
print(f"trajectory points={len(traj)}, obstacles={len(obstacles)} -> {out_path}")
