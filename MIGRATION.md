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

## 實際遷移結果(Phase 2 執行紀錄)

clone AWS repo 後逐檔檢視,實況比預期輕:

| 項目 | 預期 | 實況 |
|---|---|---|
| 模型 plugin | 可能要拆 `libgazebo_ros_*` | **14 個模型全部 plugin=0**,無需拆 |
| 材質 | 可能要把 `<material><script>` 轉 PBR | **全部無 material script**,材質靠 `.DAE` 自帶貼圖 → 不需改 |
| world plugin | 倉庫 world 幾乎無 plugin | 確認:**world 完全沒有 Classic plugin**,只有 include + 一盞 point light + physics |
| 靜態 | — | 14 個模型皆 `<static>1`,利於 SLAM(不會被撞動) |
| mesh | 通用 | Collada `.DAE`(visual + collision 各一),原封沿用 |

**實際動到的**:
1. 28 個 `model.sdf` / `model.config`:`sdf version` 1.6 → 1.10(含一個用單引號 `version='1.6'` 的 Bucket_01)。
2. 2 個 world(`small_warehouse`、`no_roof_small_warehouse`):升版、清 `frame=""`/`frame=''`、physics 去 `type="ode"`、補 4 個 world 系統 plugin + `<scene>`。
3. 30 個 XML 檔全數通過良構檢查;**尚未在 gz sim 實機載入**。

## 驗證(本機 + GitHub Actions)

遷移後分兩層把關(你本機 CPU 吃緊,主力交給 CI):

- **輕量靜態驗證** [`scripts/validate.sh`](scripts/validate.sh)(只解析、不跑物理/渲染,CPU 吃很少):14 個 `model.sdf` 過 `gz sdf -k`、2 個 world XML 良構、world 裡每個 `model://` 都對應得到 `models/<name>/`。
- **headless 真載入** [`.github/workflows/validate.yml`](.github/workflows/validate.yml) 在 GitHub 的 Harmonic 上跑 `gz sim -s -r --iterations 300`——**唯一能真正解析 `model://`、載入整個 world 的方式**。

> 為什麼不能只用 `gz sdf -p` 驗 world:`model://` 是 gz-sim 執行期 + `GZ_SIM_RESOURCE_PATH` 的功能,獨立 sdformat 工具沒註冊 findFile callback(會報 "callback is empty"),include 解析只能交給 `gz sim`。

**驗證過程抓到的真 bug(都已修)**:
1. `<physics>` 的 `type` 是 SDFormat **必填屬性**——一開始把 `type="ode"` 整個拿掉,導致 world 驗證 Error 4;改回保留字串(實際引擎由 `gz-sim-physics-system` 預設 dartsim 決定)。
2. `GroundB`、`RoofB` 的慣性張量**違反三角不等式**(AWS 原始資料就錯),新版 sdformat 報 Error 19;兩者皆 static,改成合法值、不影響模擬。
3. XML 註解內不可有 `--`(雙連字號):我寫的註解含 `--physics-engine`,被嚴格 XML 解析器(expat)拒(tinyxml2 容忍但不可攜),已改寫。
4. `frame=""` pose 屬性(Bucket/RoofB)在新 sdformat 是 warning,一併清掉。

> 心得:`gz sdf` 與嚴格 XML 解析器(expat)各抓到不同問題,兩個一起用才完整。這也是「先在本機跑驗證、再寫 CI」的價值——CI 腳本本身的盲點先在本機補掉。

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
