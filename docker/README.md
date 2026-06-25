# docker/

ROS 2 Jazzy + Gazebo Harmonic 的容器環境(**晚點實作**)。

規劃:
- `Dockerfile`:基於 `osrf/ros:jazzy-desktop-full`,加裝 `ros-jazzy-ros-gz`(帶 Harmonic)、`ros-jazzy-slam-toolbox`、`ros-jazzy-nav2-bringup`、`ros-jazzy-teleop-twist-keyboard`。
- `run.sh` / `compose.yaml`:掛載本 repo、設 `GZ_SIM_RESOURCE_PATH`、headless(Xvfb / `--headless-rendering`,僅 ogre2)與 GUI 兩種模式。

> 不在主機裝 ROS;主機現有的是 Gazebo Jetty(gz-sim 10),容器內自帶 Harmonic,互不干擾。
