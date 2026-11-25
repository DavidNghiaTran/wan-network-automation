import os
import time
from datetime import datetime
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result

ARCHIVE_DIR = "backups/archive"
LATEST_DIR = "backups/latest"

def backup_config(task: Task) -> Result:
    output = task.run(
        task=netmiko_send_command,
        command_string="show running-config"
    )
    
    # Lọc bỏ dòng động "Current configuration : xxx bytes" và NTP clock để tránh báo Drift giả
    lines = [
        line for line in output.result.splitlines()
        if not line.startswith("Current configuration") and not line.startswith("! Last configuration")
    ]
    clean_config = "\n".join(lines) + "\n"

    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(LATEST_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_file = f"{ARCHIVE_DIR}/{task.host.name}_{timestamp}.txt"
    latest_file = f"{LATEST_DIR}/{task.host.name}.cfg"

    with open(archive_file, "w", encoding="utf-8") as f:
        f.write(clean_config)
    with open(latest_file, "w", encoding="utf-8") as f:
        f.write(clean_config)

    return Result(host=task.host, result=f"Backed up -> {latest_file}")

def main():
    start_time = time.perf_counter()
    nr = InitNornir(config_file="config.yaml")
    results = nr.run(task=backup_config)
    print_result(results)
    elapsed = time.perf_counter() - start_time
    print(f"=== TONG THOI GIAN SAO LUU 8 THIET BI (NORNIR): {elapsed:.3f} GIAY ===")

if __name__ == "__main__":
    main()
