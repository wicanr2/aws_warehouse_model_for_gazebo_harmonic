# models/

從 [aws-robotics/aws-robomaker-small-warehouse-world](https://github.com/aws-robotics/aws-robomaker-small-warehouse-world) 搬來、並遷移到 Harmonic 的倉庫模型(Phase 2)。

- 各模型保留 `meshes/`(mesh 通用)、`model.config`;`model.sdf` 升版、移除 Classic 標籤、材質改 mesh 自帶 / PBR。
- 搬入時連同原 repo `LICENSE` 與出處一併保留(見 [../NOTICE](../NOTICE))。
- `model://aws_robomaker_warehouse_*` 由 `GZ_SIM_RESOURCE_PATH` 指到本目錄解析。
