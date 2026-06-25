# aws_warehouse_model_for_gazebo_harmonic

把 **AWS RoboMaker Small Warehouse** 世界從 **Gazebo Classic** 機械遷移到 **新版 Gazebo(Harmonic / gz sim)**,並附一台自搭的**差速搬運車 AMR**(非 turtlebot3)與 **slam_toolbox** 線上建圖,跑在 **ROS 2 Jazzy** 上。

> 目前狀態:**骨架(scaffold)**。目錄與計畫已就位,實作(模型遷移、Docker、launch)分階段填入,見下方進度表。

---

## 這個 repo 在做什麼

AWS 官方的 [aws-robomaker-small-warehouse-world](https://github.com/aws-robotics/aws-robomaker-small-warehouse-world) 是給 **Gazebo Classic**(Gazebo 7/9)的;Classic 已於 2025-01-31 EOL。本 repo 把它**機械遷移**到新版 Gazebo,讓它能在 ROS 2 Jazzy + Gazebo Harmonic 上載入,並搭一台差速搬運車跑 SLAM。

「機械遷移」而非重寫:倉庫本身 95% 是**靜態幾何**(地板/牆/貨架/棧板的 mesh),mesh 兩套 Gazebo 通用;真正要改的是**資源路徑、SDF 版本、plugin、world 系統 plugin、材質**這幾項機械性差異。完整清單見 [MIGRATION.md](MIGRATION.md)。

## 版本基準

| 項目 | 選定 | 理由 |
|---|---|---|
| ROS 2 | **Jazzy**(Ubuntu 24.04) | 官方配對 Gazebo Harmonic |
| Gazebo | **Harmonic(gz-sim 8)** | Jazzy 官方搭檔;透過 `ros-jazzy-ros-gz` vendor 套件安裝 |
| 執行 | **Docker** | 不污染主機(主機現裝的是更新的 Gazebo Jetty / gz-sim 10,官方搭檔是 Rolling) |

> 為什麼不直接用主機的 Jetty:Jetty(gz-sim 10)官方配對 ROS 2 Rolling,不是 Jazzy;Jazzy + Jetty 不在官方支援組合上。容器內用 Harmonic,主機那顆 Jetty 不動。

## 與 robot-notes 的關係

- **本 repo**:放**可跑/可改的實作產物**(遷移後的 world/models、Docker、AMR URDF、launch、設定、腳本)。
- **[robot-notes](https://github.com/wicanr2/robot-notes)**:放**純技術文件**——把整套寫成可重跑教學,連結回本 repo。

## 目錄結構

```
.
├── README.md            # 本檔
├── MIGRATION.md         # ★ Classic → Harmonic 機械遷移清單(Phase 2 工作依據)
├── docker/              # Dockerfile / 執行腳本(Jazzy + Harmonic;晚點實作)
├── worlds/              # 遷移後的世界檔 small_warehouse.sdf
├── models/              # ★ 從 AWS repo 搬來、路徑/SDF/材質已遷移的倉庫模型
├── robot/forklift/      # ★ 舵輪驅動叉車(tricycle,方塊車身)+ gz 原生控制 plugin
├── launch/              # warehouse / spawn / slam / bringup launch
├── config/              # ros_gz_bridge、slam_toolbox、RViz 設定
└── scripts/             # validate.sh、check_moved.py 等
```

## 進度

| Phase | 內容 | 狀態 |
|---|---|---|
| 1 | Scaffold:目錄、README、遷移清單 | ✅ 完成 |
| 2 | **AWS warehouse 機械遷移**(搬 14 models + 2 worlds) | ✅ 完成 |
| 2b | 驗證:`validate.sh` + GitHub Actions(Harmonic) | ✅ CI 全綠(靜態驗證 + `gz sim` headless 真載入都過) |
| 3 | **舵輪叉車(純 gz 能動)**:tricycle 結構 + gz plugin + 會動測試 | ✅ CI 實測會動(headless 位移 ~0.56m) |
| 1b | Docker 基底(Jazzy + ros-jazzy-ros-gz + slam_toolbox) | ⏸ 晚點實作 |
| 4 | 串接 launch / ros2_control(換 ROS 2)、spawn 進倉庫 | ⬜ 待做 |
| 5 | slam_toolbox + 繞圈 + 截圖 | ⬜ 待做(實跑) |

### Phase 3 舵輪叉車(robot/forklift/)

reach-truck 構型:**一顆可轉向+驅動的舵輪(後)+ 兩顆從動承載輪(前,叉子端)+ 可升降叉子**。用 **gz 原生 plugin**(JointController / JointPositionController),**純 Gazebo 即可驅動,不需 ROS 2**:

```bash
gz topic -t /forklift/traction -m gz.msgs.Double -p 'data: 8.0'   # 舵輪轉速 rad/s
gz topic -t /forklift/steer    -m gz.msgs.Double -p 'data: 0.4'   # 舵角 rad
gz topic -t /forklift/fork     -m gz.msgs.Double -p 'data: 0.3'   # 叉子高度 m
```

先方塊車身求「會動」;`worlds/forklift_test.sdf` 是測試平地。CI 的 `forklift-move` job 會 headless 載入、下指令、比對前後位姿確認真的有移動。外觀之後可換 Fuel OpenRobotics/Forklift mesh,運動學換成 ros2_control 的 `tricycle_controller`(進 ROS 2 階段)。

### Phase 2 已遷移內容

- `models/`：14 個 AWS 倉庫模型(貨架/牆/地板/雜物/棧板車…),含 `meshes/*.DAE` 與貼圖,**原封搬入**;每個 `model.sdf` / `model.config` 的 SDF 版本 1.6 → 1.10。
- `worlds/small_warehouse.sdf`、`worlds/no_roof_small_warehouse.sdf`：由原 `.world` 機械遷移——升 SDF 版本、清 `frame=""`、physics 去掉 `type="ode"`(改用 Harmonic 預設 dartsim)、補 4 個 world 系統 plugin + `<scene>`。
- 意外輕鬆:14 個模型**全部 `plugin=0`、無 `<material><script>`、全 `<static>`**,材質靠 DAE 自帶貼圖 → 模型層只需升版,不需改材質或拆 plugin。
- 全 30 個 XML 檔通過良構檢查。**尚未在 gz sim 實際載入**(Docker 未建),材質顯示、Sensors plugin 名等待實跑校正。
- 來源授權:AWS 原始 LICENSE(MIT)存於 `models/LICENSE.aws`,出處見 [NOTICE](NOTICE)。

## 驗證

不確定模型/世界改對了沒,跑驗證即可(本機 CPU 吃緊就交給 GitHub Actions,push 後自動跑):

- 本機輕量檢查(只解析、不跑物理/渲染):
  ```bash
  bash scripts/validate.sh
  ```
  檢查所有 `model.sdf`(`gz sdf -k`,含 14 倉庫模型 + 叉車)、worlds XML 良構、每個 `model://` 都對應得到 `models/` 或 `robot/` 下的目錄。
- **GitHub Actions**([`.github/workflows/validate.yml`](.github/workflows/validate.yml)):在 Gazebo Harmonic 上跑靜態驗證、`gz sim` headless 真正載入 world(唯一能解析 `model://`),以及 `forklift-move`(載入叉車、下指令、確認位姿有變=真的會動)。這幾項**不需 render**,在免費 runner 上 100% 可靠。
- `render` / `video` job(成果圖、錄影)**需要 render**:免費 runner 無 GPU、純軟體渲染(EGL + `GALLIUM_DRIVER=llvmpipe`)又慢又間歇,設為 `continue-on-error`(不擋 CI)、屬 best-effort。穩定出圖要 GPU runner / 帶 GL 的 Docker / 本機一次性截圖。技術細節與雷見 [robot-notes 教學 §7](https://github.com/wicanr2/robot-notes/blob/main/docs/50-physical-ai/simulation-gazebo-ros2.md)。

驗證細節與一路抓到的真 bug(physics type 必填、慣性違反三角不等式、XML 註解 `--`…)見 [MIGRATION.md](MIGRATION.md)。

## 怎麼跑

待 Docker 與 launch 完成後補上。屆時大致為:`docker build` → 起容器 → `ros2 launch ... bringup.launch.py` → RViz 看建圖。

## 來源與授權

- 倉庫模型衍生自 [aws-robotics/aws-robomaker-small-warehouse-world](https://github.com/aws-robotics/aws-robomaker-small-warehouse-world)。搬入 `models/` 時一併納入其原始 LICENSE 與出處標註(原授權以該 repo `LICENSE` 為準,待 Phase 2 搬入時確認)。
- 遷移方法、ROS 2 / Gazebo 版本對應等技術出處見 [MIGRATION.md](MIGRATION.md) 與 robot-notes。
