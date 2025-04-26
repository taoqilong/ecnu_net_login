# ecnu_net_login
用于在linux环境下登录华东师范大学校园网的python脚本

## Installation
下载或者 clone 本仓库
```bash
git clone https://github.com/taoqilong/ecnu_net_login.git
```

## Usage
1.  **配置信息:**
    打开`LoginECNU_v2.py` 文件，修改你的校园网用户名和密码:
    ```python
    # --- Configuration ---
    USERNAME = "YOUR_ECNU_USERNAME" # Replace with your actual username, usually student ID number
    PASSWORD = "YOUR_ECNU_PASSWORD" # Replace with your actual password
    # -------------------
    ```

2.  **运行脚本:**
    导航到脚本所在文件夹，运行脚本:
    ```bash
    cd ecnu_net_login
    python LoginECNU_v2.py
    ```
