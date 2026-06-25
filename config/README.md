# config/

設定檔(Phase 4–5)。

- `bridge.yaml` — `ros_gz_bridge` topic 對應(`/scan` LaserScan、`/odom` Odometry、`/cmd_vel` Twist、`/clock`、`/tf`)
- `slam_toolbox.yaml` — `mapper_params_online_async`(`odom_frame=odom`、`map_frame=map`、`base_frame=base_footprint`、`scan_topic=/scan`)
- `slam.rviz` — RViz2 設定:Fixed Frame=`map`,Display 加 Map(`/map`)、LaserScan(`/scan`)、TF、RobotModel、(可選 Path/PoseGraph)
