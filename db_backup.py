"""
db_backup.py
Автоматизированный дамп БД + скачивание.
Поддерживает зашифрованные SSH-ключи (читает SSH_KEY_PASSWORD из .env 
или просит интерактивно).
Использует posixpath для формирования удалённых путей.
Совместимо с Python 3.9.
"""
import sys
import time
from datetime import datetime
from pathlib import Path
import posixpath
import getpass
from typing import Optional

try:
    import paramiko
except ImportError:
    print("Требуется библиотека paramiko. Установи её: pip install paramiko")
    sys.exit(1)


def read_env(path: Path):
    data = {}
    if not path.exists():
        return data
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            data[key.strip()] = val.strip().strip('"').strip("'")
    return data


HERE = Path(__file__).resolve().parent
ENV = read_env(HERE / ".env")

# ИЗМЕНЕНИЯ: новый сервер и путь
SSH_HOST = ENV.get("SSH_HOST", "109.73.206.39")
SSH_USER = ENV.get("SSH_USER", "root")
SSH_KEY_PATH = ENV.get("SSH_KEY_PATH", "D:/Dev/vm_access/id_ed25519")
SSH_KEY_PASSWORD = ENV.get("SSH_KEY_PASSWORD", None)
SSH_PASSWORD = ENV.get("SSH_PASSWORD", None)
REMOTE_PROJECT_DIR = ENV.get("REMOTE_PROJECT_DIR", "/opt/cuckoo_pump")
CONTAINER_NAME = ENV.get("CONTAINER_NAME", "cuckoo_pump_db")
DB_USER = ENV.get("DB_USER", "postgres")
DB_NAME = ENV.get("DB_NAME", "cuckoo")
LOCAL_BACKUP_DIR = ENV.get(
    "LOCAL_BACKUP_DIR", str(Path("D:/DB_backup/cuckoo_pump"))
)
DATE_IN_NAME = ENV.get("DATE_IN_NAME", "true").lower() in \
               ("1", "true", "yes", "on")
REMOVE_REMOTE_AFTER_DOWNLOAD = ENV.get("REMOVE_REMOTE_AFTER_DOWNLOAD",
                                       "false").lower() in \
                               ("1", "true", "yes", "on")

filename = f"backup_{datetime.now().strftime('%Y-%m-%d')}.sql" \
    if DATE_IN_NAME else "backup.sql"
REMOTE_DUMP_PATH = posixpath.join(REMOTE_PROJECT_DIR.rstrip("/"), filename)
LOCAL_BACKUP_DIR = Path(LOCAL_BACKUP_DIR)
LOCAL_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DUMP_PATH = LOCAL_BACKUP_DIR / filename


def load_private_key_with_possible_passphrase(path: Path,
                                              passphrase: Optional[str]):
    last_exc = None
    loaders = [paramiko.RSAKey.from_private_key_file]
    if hasattr(paramiko, "Ed25519Key"):
        loaders.append(paramiko.Ed25519Key.from_private_key_file)
    if hasattr(paramiko, "ECDSAKey"):
        loaders.append(paramiko.ECDSAKey.from_private_key_file)
    if hasattr(paramiko, "DSSKey"):
        loaders.append(paramiko.DSSKey.from_private_key_file)

    for loader in loaders:
        try:
            if passphrase is not None:
                return loader(str(path), password=passphrase)
            return loader(str(path))
        except paramiko.ssh_exception.PasswordRequiredException as e:
            last_exc = e
            continue
        except Exception as e:
            last_exc = e
            continue

    if last_exc:
        raise last_exc
    raise RuntimeError("Не удалось загрузить SSH-ключ: неизвестный формат.")


def connect_ssh(host,
                user,
                key_path=None, key_passphrase: Optional[str] = None,
                password=None, timeout=30):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        pkey = None
        if key_path:
            key_path_obj = Path(key_path).expanduser()
            if key_path_obj.exists():
                try:
                    pkey = load_private_key_with_possible_passphrase(
                        key_path_obj, None)
                except paramiko.ssh_exception.PasswordRequiredException:
                    if key_passphrase is None:
                        key_passphrase = getpass.getpass(
                            "SSH key is encrypted. Enter passphrase: ")
                    pkey = load_private_key_with_possible_passphrase(
                        key_path_obj, key_passphrase)
        if pkey:
            client.connect(hostname=host, username=user, pkey=pkey,
                           timeout=timeout)
        else:
            client.connect(hostname=host, username=user, password=password,
                           timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"Не удалось подключиться по SSH: {e}")
    return client


def run_remote_dump(ssh_client, container, db_user, db_name,
                    remote_output_path, sudo_password=None):
    cmd = f"sudo sh -c 'docker exec {container} pg_dump -U {db_user} " \
          f"{db_name} > {remote_output_path}'"
    stdin, stdout, stderr = ssh_client.exec_command(
        cmd, get_pty=True, timeout=600
    )
    if sudo_password:
        try:
            stdin.write(sudo_password + "\n")
            stdin.flush()
        except Exception:
            pass
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode(errors="ignore")
    err = stderr.read().decode(errors="ignore")
    return exit_status, out, err


def download_file_sftp(ssh_client, remote_path, local_path):
    sftp = ssh_client.open_sftp()
    try:
        sftp.get(remote_path, str(local_path))
    finally:
        sftp.close()


def remove_remote_file(ssh_client, path):
    cmd = f"rm -f {path}"
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    return stdout.channel.recv_exit_status()


def main():
    print("=== DB backup script ===")
    print(f"SSH host: {SSH_USER}@{SSH_HOST}")
    print(f"Remote project dir: {REMOTE_PROJECT_DIR}")
    print(f"Container: {CONTAINER_NAME}")
    print(f"DB: {DB_NAME} (user {DB_USER})")
    print(f"Remote dump path: {REMOTE_DUMP_PATH}")
    print(f"Local path: {LOCAL_DUMP_PATH}")
    print("Connecting to SSH...")

    try:
        ssh = connect_ssh(SSH_HOST, SSH_USER,
                          key_path=SSH_KEY_PATH,
                          key_passphrase=SSH_KEY_PASSWORD,
                          password=SSH_PASSWORD)
    except Exception as e:
        print("Ошибка подключения SSH:", e)
        sys.exit(2)

    try:
        print("Создаю дамп на сервере (в контейнере)...")
        exit_code, out, err = run_remote_dump(
            ssh, CONTAINER_NAME, DB_USER, DB_NAME, REMOTE_DUMP_PATH,
            sudo_password=SSH_PASSWORD)
        if exit_code != 0:
            print("Ошибка при создании дампа (exit code != 0).")
            print("stdout:", out)
            print("stderr:", err)
            ssh.close()
            sys.exit(3)
        print("Дамп успешно создан на сервере.")
        time.sleep(1)

        print("Скачиваю дамп по SFTP...")
        try:
            download_file_sftp(ssh, REMOTE_DUMP_PATH, LOCAL_DUMP_PATH)
        except Exception as e:
            print("Ошибка при скачивании файла:", e)
            ssh.close()
            sys.exit(4)
        print(f"Дамп скачан локально: {LOCAL_DUMP_PATH}")

        if REMOVE_REMOTE_AFTER_DOWNLOAD:
            print("Удаляю дамп на сервере...")
            rc = remove_remote_file(ssh, REMOTE_DUMP_PATH)
            if rc == 0:
                print("Удаление удалённого файла выполнено.")
            else:
                print("Не удалось удалить удалённый файл (код возврата:", rc,
                      ")")
    finally:
        ssh.close()
    print("Готово.")


if __name__ == "__main__":
    main()
