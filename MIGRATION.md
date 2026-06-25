# AWS Small Warehouse:Gazebo Classic → Harmonic 機械遷移清單

這份是 Phase 2 的工作依據:把 [aws-robotics/aws-robomaker-small-warehouse-world](https://github.com/aws-robotics/aws-robomaker-small-warehouse-world)(Gazebo Classic)的世界與模型,搬到新版 Gazebo(**Harmonic / gz-sim 8**)能載入的形式。

> 核心觀念:**不是重寫,是機械遷移**。倉庫 95% 是靜態幾何,mesh(Collada/OBJ/STL)兩套 Gazebo 通用;卡住的是下列幾項機械性差異,逐項改即可。

---

## 為什麼 Classic 的 `.world` 不能直接在 gz sim 跑

| # | 卡點 | Classic | 新 gz sim(Harmonic) | 來源 |
|---|---|---|---|---|
| ① | 資源路徑環境變數 | `GAZEBO_MODEL_PATH` | **`GZ_SIM_RESOURCE_PATH`**(解析 `model://` 與 `<include><uri>`) | [gz resources](https://gazebosim.org/api/sim/8/resources.html) |
| ② | plugin 不相容 | `libgazebo_ros_*` | **`gz-sim-*-system`**,且 `name=` 要填 C++ 類別全名;硬載對方 plugin 會 crash | [migration SDF](https://gazebosim.org/api/sim/8/migrationsdf.html) |
| ③ | world 缺系統 plugin | Classic 內建 | 要自掛 Physics / SceneBroadcaster / UserCommands / Sensors | [sdf_worlds](https://gazebosim.org/docs/latest/sdf_worlds/) |
| ④ | SDF 版本與棄用標籤 | 常為 `<sdf version="1.6">` | 升到 Harmonic 接受的版本,檢查棄用標籤 | [migration SDF](https://gazebosim.org/api/sim/8/migrationsdf.html) |
| ⑤ | 材質 | `<material><script>`(Gazebo 材質腳本) | ogre2 / PBR;Classic 材質腳本常不顯示 → 靠 mesh 自帶材質或改 PBR | [sensors/rendering](https://gazebosim.org/docs/latest/sensors/) |

> 好消息:倉庫 **world 本身幾乎沒有 plugin**(就 `<include>` 一堆靜態模型 + 太陽 + 地面),所以②在 world 層幾乎不用動;帶 plugin 的是「機器人」(diff drive、LiDAR),那本來就為 gz 另寫(見 `robot/`)。

---

## 遷移步驟(逐項)

1. **取得原始資產**
   - clone `aws-robotics/aws-robomaker-small-warehouse-world`,取 `models/` 與 `worlds/small_warehouse.world`。
   - 連同其 `LICENSE` 一起搬入本 repo `models/`,保留出處標註。

2. **搬 models/**(本 repo `models/`)
   - 各模型的 mesh(`meshes/*.dae` 等)直接沿用。
   - 檢查每個 `model.sdf`:升 SDF 版本、移除 Classic 專屬標籤/plugin、材質改走 mesh 自帶或 PBR。
   - `model.config` 保留(gz 也讀)。

3. **改世界檔**(本 repo `worlds/small_warehouse.sdf`)
   - 升 `<sdf version>`(④)。
   - 移除任何 Classic plugin 段(②);倉庫 world 通常很少或沒有。
   - **加上 world 層系統 plugin**(③):
     ```xml
     <plugin filename="gz-sim-physics-system"           name="gz::sim::systems::Physics"/>
     <plugin filename="gz-sim-user-commands-system"     name="gz::sim::systems::UserCommands"/>
     <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
     <plugin filename="gz-sim-sensors-system"           name="gz::sim::systems::Sensors">
       <render_engine>ogre2</render_engine>
     </plugin>
     ```
     > LiDAR 要出資料**一定**要 Sensors system。Sensors 段的精確 filename/name **待實機驗證後定稿**。

4. **設資源路徑**(①)
   - `export GZ_SIM_RESOURCE_PATH=<本 repo>/models`,讓 `model://aws_robomaker_warehouse_*` 解析得到。

5. **驗證載入**
   - 容器內 `gz sim worlds/small_warehouse.sdf` 能開、貨架/牆在、無 plugin crash、材質正常(非全灰)。

6. **機器人另外來**
   - 自搭差速搬運車的 diff drive / `gpu_lidar` 用 gz 原生 plugin 寫(見 `robot/carrier_amr/`),spawn 進此世界。

---

## 待查證 / 待實機校正(不寫死)

- world 層 `gz-sim-sensors-system` 的精確 filename/name(依命名規律推得)。
- 各 AWS 模型 SDF 在 Harmonic 下的材質顯示(可能要逐個調 PBR)。
- AWS warehouse 原始 LICENSE 與條款(搬入時確認並保留)。
- 是否有官方掛名的 AWS warehouse Harmonic 移植(目前查到官方只到 Classic;本 repo 即為自行遷移)。

## 參考

- AWS repo(Classic):https://github.com/aws-robotics/aws-robomaker-small-warehouse-world
- Classic→gz 遷移(SDF/plugin):https://gazebosim.org/api/sim/8/migrationsdf.html
- gz 資源路徑:https://gazebosim.org/api/sim/8/resources.html
- world 系統 plugin:https://gazebosim.org/docs/latest/sdf_worlds/
- Fuel 模型 include:https://gazebosim.org/docs/harmonic/fuel_insert/
- ROS 2 ↔ Gazebo 安裝/配對:https://gazebosim.org/docs/latest/ros_installation/
