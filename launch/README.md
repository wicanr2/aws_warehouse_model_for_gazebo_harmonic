# launch/

ROS 2 launch 檔(Phase 4)。

- `warehouse.launch.py` — 起 gz sim 載 `worlds/small_warehouse.sdf`
- `spawn_amr.launch.py` — spawn 搬運車 + `robot_state_publisher` + `ros_gz_bridge`(/scan /odom /cmd_vel /tf /clock)
- `slam.launch.py` — `slam_toolbox online_async`(吃 /scan + odom→base_link,出 /map + map→odom),`use_sim_time:=true`
- `bringup.launch.py` — 一鍵組合上面三者

tf 鏈目標:`map → odom → base_footprint → base_link → {wheels, laser}`。
