import argparse
from pathlib import Path

EXCLUDED_ITEMS = {'__pycache__', 'venv', '.venv'}


def print_project_structure(
        start_path=".", indent="", max_depth=3, current_depth=0
):
    if current_depth > max_depth:
        return

    try:
        items = sorted(
            Path(start_path).iterdir(),
            key=lambda x: (not x.is_dir(), x.name.lower())
        )

        for i, item in enumerate(items):
            # Пропускаем скрытые файлы и папки
            if item.name.startswith('.') or item.name in EXCLUDED_ITEMS:
                continue

            is_last = i == len(items) - 1
            prefix = "└── " if is_last else "├── "
            connector = "    " if is_last else "│   "

            print(f"{indent}{prefix}{item.name}")

            if item.is_dir():
                print_project_structure(
                    item,
                    indent + connector,
                    max_depth,
                    current_depth + 1
                )
    except PermissionError:
        print(f"{indent}└── [Permission denied]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Print project structure')
    parser.add_argument(
        'path', nargs='?', default='.', help='Path to project directory'
    )
    parser.add_argument('--depth', type=int, default=5, help='Maximum depth')

    args = parser.parse_args()

    print(f"Project structure: {args.path}")
    print_project_structure(args.path, "", args.depth, 0)
