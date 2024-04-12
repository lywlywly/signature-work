import subprocess

def fetch_html_headless_chrome(url: str, output_file_name: str = "out.html"):
    executable = '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'
    user_agent = '"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"'
    url = f'"{url}"'
    command = f"{executable} --headless --disable-gpu --dump-dom --user-agent={user_agent} {url} > {output_file_name}"
    subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
