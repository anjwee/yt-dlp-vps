# 媒体下载与处理脚本

这是一个基于 `yt-dlp` 和 `ffmpeg` 的 Python 命令行工具，旨在简化从网络下载音视频、合并以及格式转换的流程。

## 特点

-   **全手动控制**：提供高级选项菜单，允许用户手动设置 Player Client, PO Token, Cookies 和代理，以应对复杂的下载环境。
-   **智能流程**：支持分离下载音视频后自动合并，或对已存在的文件进行格式转换。
-   **播放列表处理**：内置开关，可以轻松选择是下载整个播放列表还是仅下载单个视频。
-   **交互式菜单**：通过简单的命令行菜单完成所有操作，无需记忆复杂的 `yt-dlp` 参数。
-   **可添加Cookies**：解决人机测试
-   **设置Proxy**：国内服务器可下载

## 依赖

在运行此脚本前，请确保您的系统已经安装了以下程序：

1.  **Python 3**
2.  **yt-dlp**: [官方安装指南](https://github.com/yt-dlp/yt-dlp#installation)
    ```bash    
    pip3 install yt-dlp   
    ```
3.  **ffmpeg**: [官方下载页面](https://ffmpeg.org/download.html) (对于合并文件和格式转换是必需的)

## 如何使用

1.  将脚本 `downloader.py` 下载。
    ```bash
    wget https://raw.githubusercontent.com/anjwee/yt-dlp-vps/refs/heads/main/downloader.py
    ```
2.  在终端中给脚本添加执行权限：
    ```bash
    chmod +x downloader.py
    ```
3.  运行脚本：
    ```bash
    python3 downloader.py
    ```
4.  根据提示输入文件名和目标 URL。
5.  在“高级下载选项”菜单中，根据您的需求配置参数（例如，为公开的 YT 视频设置 Player Client 为 `ios`）。
6.  进入“功能选择”菜单，选择您想要执行的操作。
7.  输入两个文件名（用','逗号隔开)'音频名,视频名'必须用英文

![适合国内使用](https://telegraph-image-btj.pages.dev/file/AgACAgUAAyEGAAS2iY3HAAMDaKLQPjEnoxIV3Q2dR1mJ-XJ4su4AAnrEMRuJDhhVx2Ab2AZyQFQBAAMCAAN5AAM2BA.png)

## 配置

脚本顶部的路径变量可以根据您的需求进行修改：

-   `TEMP_DOWNLOAD_PATH`: 下载和处理过程中的临时文件存放位置。
-   `MUSIC_LIBRARY_PATH`: 转换后的 MP3 文件最终存放位置。

## 许可

本项目采用 [MIT 许可证](LICENSE)。
