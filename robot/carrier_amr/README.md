# robot/carrier_amr/

自搭的差速搬運車 AMR(**非 turtlebot3**,Phase 3)。

最小組成(對應 robot-notes `sdf-3d-models.md` 的搬運車範例):
- 車體 box + 左右驅動輪(continuous joint)+ 一個 caster(萬向輪)
- 2D LiDAR:`gpu_lidar` sensor → `/scan`
- `gz-sim-diff-drive-system` plugin → 收 `/cmd_vel`、發 `/odom` 與 `odom→base_link` tf
  - 必填:`left_joint` / `right_joint` / `wheel_separation` / `wheel_radius`
  - ⚠ 注意 Gazebo DiffDrive 吃 `gz.msgs.Twist`(無 stamp),Jazzy 上游 `diff_drive_controller`/Nav2 預設 `TwistStamped`,bridge 對接需校正(待實跑)

> 之後若要 sim-to-real 共用 controller,可改走 `gz_ros2_control` + `diff_drive_controller`(ros2_control)。
