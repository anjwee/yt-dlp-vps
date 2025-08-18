#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

# --- 1. 路径集中配置 ---
TEMP_DOWNLOAD_PATH = "/mnt/"
MUSIC_LIBRARY_PATH = "/mnt/"
# -------------------------

# 全局变量
COOKIES_FILE, PROXY, PLAYER_CLIENT, PO_TOKEN = None, None, None, None
# 【已修改】将禁止下载播放列表的开关, 默认值设为 True (开启)
DISABLE_PLAYLIST = True 

def run_command(command):
    """运行命令并实时显示输出。"""
    if command is None: return False
    print(f"运行命令: {command}")
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode == 0:
        print("命令执行成功！\n" + "-" * 40)
        return True
    else:
        print(f"命令执行失败，返回码: {result.returncode}\n" + "-" * 40)
        return False

def apply_global_options(cmd):
    """根据您在菜单中设置的全局选项来构建命令。"""
    global COOKIES_FILE, PROXY, PLAYER_CLIENT, PO_TOKEN, DISABLE_PLAYLIST
    
    if DISABLE_PLAYLIST:
        cmd += ' --no-playlist'

    if PLAYER_CLIENT:
        cmd += f' --extractor-args "youtube:player_client={PLAYER_CLIENT}"'
    if PO_TOKEN:
        cmd += f' --extractor-args "youtube:po_token={PO_TOKEN}"'
    if COOKIES_FILE:
        cmd += f' --cookies "{COOKIES_FILE}"'
    if PROXY:
        cmd += f' --proxy "{PROXY}"'
    return cmd

def find_existing_file(base_path, filename_no_ext):
    """根据文件名（不带后缀）找到存在的文件，返回完整路径（不带引号）"""
    for ext in [".mp4", ".m4a", ".webm", ".mp3", ".wav", ".opus", ".mkv"]:
        candidate = os.path.join(base_path, filename_no_ext + ext)
        if os.path.exists(candidate):
            return candidate
    return None

def generate_command1(arguments):
    """生成查询命令"""
    return apply_global_options(f'yt-dlp --list-formats "{arguments}"')

def generate_command2(audio_name, video_name, arguments, audio_format, video_format):
    """生成音视下载命令"""
    audio_format = audio_format if audio_format else "140"
    video_format = video_format if video_format else "137"
    audio_cmd = apply_global_options(
        f'yt-dlp -f {audio_format} -o "{TEMP_DOWNLOAD_PATH}{audio_name}.%(ext)s" "{arguments}"'
    )
    video_cmd = apply_global_options(
        f'yt-dlp -f {video_format} -o "{TEMP_DOWNLOAD_PATH}{video_name}.%(ext)s" "{arguments}"'
    )
    return f'{audio_cmd} && \\\n{video_cmd}'

def generate_command3(audio_name, video_name, extra_filenames=None):
    """生成音视合并命令"""
    if extra_filenames:
        parts = [f.strip() for f in extra_filenames.split(",") if f.strip()]
        if len(parts) != 2:
            print("错误：需要输入两个用逗号隔开的文件名。")
            return None
        f_audio, f_video = parts
    else:
        f_audio, f_video = audio_name, video_name

    input_audio_path = find_existing_file(TEMP_DOWNLOAD_PATH, f_audio)
    input_video_path = find_existing_file(TEMP_DOWNLOAD_PATH, f_video)
    
    if not input_audio_path or not input_video_path:
        print(f"错误：合并失败，找不到 {f_audio} 或 {f_video} 的对应媒体文件。")
        return None

    output_filename_base = f"{Path(input_audio_path).stem}{Path(input_video_path).stem}"
    output_file = f'"{os.path.join(TEMP_DOWNLOAD_PATH, output_filename_base)}.mp4"'
    
    input_file_audio = f'"{input_audio_path}"'
    input_file_video = f'"{input_video_path}"'
    rm_files = f'{input_file_audio} {input_file_video}'

    print(f"合并文件：{input_file_video} 和 {input_file_audio}")
    return f'''ffmpeg -i {input_file_video} -i {input_file_audio} \\
-c:v copy -c:a copy {output_file} && \\
rm {rm_files}'''

def generate_command5(video_name, arguments, video_format):
    """生成仅下载视频命令"""
    video_format = video_format if video_format else "137"
    return apply_global_options(f'yt-dlp -f {video_format} -o "{TEMP_DOWNLOAD_PATH}{video_name}.%(ext)s" "{arguments}"')

def download_and_convert(dl_type, audio_name, arguments, format_code):
    """分步下载并转换功能"""
    dl_cmd = ""
    if dl_type == 'mp3':
        format_code = format_code if format_code else "140"
        dl_cmd = apply_global_options(
            f'yt-dlp -f {format_code} -o "{TEMP_DOWNLOAD_PATH}{audio_name}.%(ext)s" "{arguments}"'
        )
    elif dl_type == 'wav':
        format_code = format_code if format_code else "137"
        dl_cmd = apply_global_options(
            f'yt-dlp -f {format_code} -o "{TEMP_DOWNLOAD_PATH}{audio_name}.%(ext)s" "{arguments}"'
        )
    
    print("--- 步骤 1/2: 开始下载 ---")
    if not run_command(dl_cmd):
        print("下载失败，转换中止。")
        return
    convert_existing_file(dl_type, audio_name)

def convert_existing_file(dl_type, audio_name):
    """直接转换已存在的文件"""
    print(f"--- 开始转换已存在的文件 '{audio_name}' ---")
    source_file = find_existing_file(TEMP_DOWNLOAD_PATH, audio_name)
    if not source_file:
        print(f"错误：找不到名为 '{audio_name}' 的源文件进行转换。")
        return

    print(f"找到源文件: {source_file}")
    target_file, convert_cmd = "", ""

    if dl_type == 'mp3':
        os.makedirs(MUSIC_LIBRARY_PATH, exist_ok=True)
        target_file = os.path.join(MUSIC_LIBRARY_PATH, f"{audio_name}.mp3")
        convert_cmd = f'ffmpeg -i "{source_file}" -y -q:a 0 "{target_file}"'
    elif dl_type == 'wav':
        target_file = os.path.join(TEMP_DOWNLOAD_PATH, f"{audio_name}.wav")
        convert_cmd = f'ffmpeg -i "{source_file}" -y -vn -acodec pcm_s16le -ar 44100 -ac 2 "{target_file}"'

    if run_command(convert_cmd):
        print("--- 清理临时文件 ---")
        try:
            os.remove(source_file)
            print(f"已删除临时文件: {source_file}")
        except OSError as e:
            print(f"删除临时文件失败: {e}")

def main():
    """主函数"""
    print("--- 媒体下载与处理工具 (完全手动控制版) ---")
    global COOKIES_FILE, PROXY, PLAYER_CLIENT, PO_TOKEN, DISABLE_PLAYLIST

    while True:
        os.makedirs(TEMP_DOWNLOAD_PATH, exist_ok=True)
        # 【已修改】每次循环开始时，将禁止播放列表重置为 True (开启)
        COOKIES_FILE, PROXY, PLAYER_CLIENT, PO_TOKEN, DISABLE_PLAYLIST = None, None, None, None, True

        filename_input = input("\n请输入文件名（支持'音频名,视频名'，直接回车退出）：").strip()
        if not filename_input: break

        if "," in filename_input:
            parts = [f.strip() for f in filename_input.split(",") if f.strip()]
            audio_name, video_name = (parts[0], parts[1]) if len(parts) == 2 else (filename_input, filename_input)
        else:
            audio_name = video_name = filename_input
            
        arguments = input("请输入媒体URL (输入q退出): ").strip()
        if not arguments or arguments.lower() == 'q': break

        while True: # 高级选项菜单
            print("\n" + "="*15 + " 高级下载选项 " + "="*15)
            print(f"  当前 Player Client : {PLAYER_CLIENT or '未设置 (默认 web)'}")
            print(f"  当前 PO Token      : {'已设置' if PO_TOKEN else '未设置'}")
            print(f"  当前 Cookie       : {COOKIES_FILE or '未设置'}")
            print(f"  当前 Proxy        : {PROXY or '未设置'}")
            print(f"  禁止下载播放列表    : {'是' if DISABLE_PLAYLIST else '否'}") # 这里会正确显示默认状态为“是”
            print("-" * 42)
            print("请选择要配置的选项：")
            print("  d - (切换)禁止下载播放列表")
            print("  p - 设置 Player Client (如: ios, mweb, tv)")
            print("  t - 设置 PO Token")
            print("  w - 加载 Cookies")
            print("  e - 设置 Proxy")
            print("  c - 清除所有高级选项")
            print("  s - 完成设置，进入功能菜单")
            print("="*42)
            
            choice = input("请输入选项: ").strip().lower()
            if choice == 's': break
            elif choice == 'd':
                DISABLE_PLAYLIST = not DISABLE_PLAYLIST
                print(f"禁止下载播放列表已{'开启' if DISABLE_PLAYLIST else '关闭'}。")
            elif choice == 'p': PLAYER_CLIENT = input("请输入 Player Client (例如: ios): ").strip()
            elif choice == 't': PO_TOKEN = input("请输入 PO Token: ").strip()
            elif choice == 'c':
                # 清除时也将禁止播放列表恢复为默认的 True
                PLAYER_CLIENT, PO_TOKEN, COOKIES_FILE, PROXY, DISABLE_PLAYLIST = None, None, None, None, True
                print("所有高级选项已清除 (禁止下载播放列表已恢复为默认开启状态)。")
            elif choice == 'w':
                default_cookies_path = "/home/cookies.txt"
                cookies = input(f"请输入 cookies.txt 路径 (回车使用 '{default_cookies_path}'): ").strip()
                COOKIES_FILE = cookies if cookies else default_cookies_path
                if os.path.exists(COOKIES_FILE): print(f"已加载: {COOKIES_FILE}")
                else: print(f"警告: 文件 '{COOKIES_FILE}' 不存在。")
            elif choice == 'e':
                default_proxy = "socks5://127.0.0.1:1080"
                proxy = input(f"请输入代理地址 (回车使用 '{default_proxy}'): ").strip()
                PROXY = proxy if proxy else default_proxy
                print(f"已设置代理: {PROXY}")
            else: print("无效选项。")

        while True: # 主功能菜单
            print("\n" + "="*15 + " 功能选择 " + "="*15)
            print("1. 查询可用格式")
            print("2. 下载音频和视频（分离）")
            print("3. 合并音频和视频")
            print("4. 下载或转换音频为MP3")
            print("5. 仅下载视频")
            print("6. 下载或转换音频为WAV")
            print("0. 返回 (输入新文件名)")
            print("="*42)

            func_choice = input("请输入选项：").strip()
            if func_choice == "1":
                run_command(generate_command1(arguments))
            elif func_choice == "2":
                audio_format = input("请输入音频编码（回车默认140）：").strip()
                video_format = input("请输入视频编码（回车默认137）：").strip()
                run_command(generate_command2(audio_name, video_name, arguments, audio_format, video_format))
            elif func_choice == "3":
                extra_filenames = input("可选：输入两个文件名（用','隔开，回车则使用默认名称合并）：").strip()
                run_command(generate_command3(audio_name, video_name, extra_filenames))
            elif func_choice == "4":
                existing_file = find_existing_file(TEMP_DOWNLOAD_PATH, audio_name)
                if existing_file:
                    convert_existing_file('mp3', audio_name)
                else:
                    audio_format = input("未找到文件，请输入音频编码以下载（回车默认140）：").strip()
                    download_and_convert('mp3', audio_name, arguments, audio_format)
            elif func_choice == "5":
                video_format = input("请输入视频编码（回车默认137）：").strip()
                run_command(generate_command5(video_name, arguments, video_format))
            elif func_choice == "6":
                existing_file = find_existing_file(TEMP_DOWNLOAD_PATH, audio_name)
                if existing_file:
                    convert_existing_file('wav', audio_name)
                else:
                    video_format = input("未找到文件，请输入视频编码以下载（回车默认137）：").strip()
                    download_and_convert('wav', audio_name, arguments, video_format)
            elif func_choice == "0":
                break
            else:
                if func_choice: print("无效选项。")

if __name__ == "__main__":
    main()