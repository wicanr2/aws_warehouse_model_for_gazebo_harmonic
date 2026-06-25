# scripts/

輔助腳本(Phase 5)。

- 遙控 / 繞圈:用 `teleop_twist_keyboard` 或自寫 `drive_loop.py` 發 `/cmd_vel`,讓搬運車繞倉庫一圈、**回到起點觸發 loop closure**,建出完整地圖。
- (實跑後)截圖輔助:headless 下 Xvfb 包 GUI,或 bridge 出 camera image 存檔。
