import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


LANGUAGES = {"ZH": "values-zh-rCN", "EN": "values", "FR": "values-fr"}
TREE_FILE_RE = re.compile(r"^tree_type_(\d+)_phase_(.+?)\.(?:png|webp)$", re.IGNORECASE)


def _read_previous_names(project_dir):
    """Reuse prior XML name keys for older IDs without a separate mapping file."""
    previous_path = project_dir / "docs" / "treeType.json"
    if not previous_path.exists():
        return {}
    with previous_path.open(encoding="utf-8") as file:
        previous = json.load(file)
    return {
        str(tree_id): item["nameXML"]
        for tree_id, item in previous.items()
        if isinstance(item, dict) and item.get("nameXML")
    }


def _discover_trees(drawable_dir, legacy_names):
    trees = {}
    for path in drawable_dir.iterdir():
        match = TREE_FILE_RE.match(path.name)
        if not match:
            continue
        tree_id, phase = match.groups()
        if "launch" in phase:
            continue
        trees.setdefault(tree_id, {"nameXML": legacy_names.get(tree_id, f"tree_type_{tree_id}"), "phases": set(), "files": []})
        trees[tree_id]["phases"].add(phase)
        trees[tree_id]["files"].append(path)
    return trees


def _copy_tree_images(sources, destination_dir):
    """Import one format per stage: WebP first, PNG only as a fallback."""
    selected = {}
    for source in sorted(sources):
        key = source.stem.lower()
        previous = selected.get(key)
        if previous is None or (source.suffix.lower() == '.webp' and previous.suffix.lower() != '.webp'):
            selected[key] = source
    for source in selected.values():
        destination = destination_dir / source.name
        shutil.copy2(source, destination)
        # Remove the older format only after its replacement has been copied.
        alternate = destination.with_suffix('.png' if source.suffix.lower() == '.webp' else '.webp')
        if alternate.is_file():
            alternate.unlink()


def _remove_replaced_pngs(directory):
    for png in directory.glob('*.png'):
        if TREE_FILE_RE.fullmatch(png.name) and png.with_suffix('.webp').is_file():
            png.unlink()


def _phase_info(phases):
    growth = sorted(int(phase) for phase in phases if phase.isdigit())
    xmas = sorted(int(phase.split("_", 1)[0]) for phase in phases if "christmas" in phase)
    if len(xmas) == 1:
        xmas *= 4
    result = {
        "hasDead": "dead" in phases,
        "hasChristmas": bool(xmas),
        "growth": growth,
    }
    if xmas:
        result["xmas"] = xmas
    result["forest"] = [growth[3]] * 4 if len(growth) == 4 else growth[-4:]
    return result


def _resource_text(root, resource_name):
    element = root.find(f"*[@name='{resource_name}']")
    return element.text if element is not None and element.text is not None else ""


def _sync_landscapes(decoded_dir, project_dir):
    """Refresh usable landscape skins, skipping text-only future releases."""
    web = project_dir / 'docs'
    themes_path = web / 'land-themes.json'
    themes = json.loads(themes_path.read_text(encoding='utf-8-sig'))
    strings = ET.parse(decoded_dir / 'res' / 'values-zh-rCN' / 'strings.xml').getroot()
    resources = {}
    density = {'mdpi': 1, 'hdpi': 2, 'xhdpi': 3, 'xxhdpi': 4, 'xxxhdpi': 5}
    for directory in sorted((decoded_dir / 'res').glob('drawable*')):
        rank = max((value for key, value in density.items() if key in directory.name.split('-')), default=0)
        for path in directory.iterdir():
            if path.suffix.lower() not in ('.webp', '.png'):
                continue
            score = (path.suffix.lower() == '.webp', rank)
            if path.stem not in resources or score > resources[path.stem][0]:
                resources[path.stem] = (score, path)

    def copy(stem, folder, name=None):
        source = resources.get(stem)
        if not source:
            return None
        source = source[1]
        destination = web / 'assets' / folder / ((name or stem) + source.suffix.lower())
        shutil.copy2(source, destination)
        alternate = destination.with_suffix('.png' if source.suffix.lower() == '.webp' else '.webp')
        if alternate.is_file():
            alternate.unlink()
        return destination.relative_to(web).as_posix()

    # Refresh backgrounds already used by the home page, preserving their URLs.
    for image in (web / 'assets' / 'ball').iterdir():
        copy(image.stem, 'ball')
    ids = {0: 'default', 1: 'xmas', 2: 'tinytan', 3: 'softpink',
           4: 'oceanblue', 5: 'creammeadow', 6: 'sunlitlime', 7: 'blossomingturf', 8: 'pineapple'}
    numbers = {0, 1} | {int(match.group(1)) for stem in resources
                              if (match := re.fullmatch(r'ground(\d+)_ground_piece', stem))}
    for number in sorted(numbers):
        prefix = f'ground{number:02d}_'
        stems = ['ground_piece', 'ground_left_side', 'ground_right_side']
        if number == 1:
            stems = ['ground_piece_xmas', 'left_xmas', 'right_xmas']
        elif number >= 2:
            stems = [prefix + stem for stem in stems]
        if not all(stem in resources for stem in stems):
            continue
        theme_id = ids.get(number, f'ground{number:02d}')
        theme = next((item for item in themes if item['id'] == theme_id), None)
        if theme is None:
            theme = {'id': theme_id, 'color': '#f4d64d' if number == 8 else '#a6cd49'}
            themes.append(theme)
        theme['name'] = _resource_text(strings, f'landskin_{number}_title') or theme.get('name', f'土地主题 {number}')
        theme['description'] = _resource_text(strings, f'landskin_{number}_description') or theme.get('description', '')
        for part, stem in zip(('tile', 'left', 'right'), stems):
            theme[part] = copy(stem, 'ground', f'{theme_id}-{part}')
        plant = theme.setdefault('plant', {})
        plant.update(name=theme['name'], sub=theme['description'])
        if number >= 3:
            ball = copy(prefix + 'plant_ball', 'ball')
            if ball:
                # New APK textures include the complete globe and its ground.
                plant.update(ball=ball, ground=None)
        elif not plant.get('ball'):
            stem = ('plant_ball', 'plant_ball_christmas', 'tinytan_plant_ball')[number]
            plant.update(ball=copy(stem, 'ball'), ground=None)
        plant.setdefault('color', 'linear-gradient(180deg,#d3f6c3,#f5efa6)' if number == 8 else 'linear-gradient(180deg,#A3D9C6,#74B29D)')
        if number == 1:
            plant['snow'] = True
    themes_path.write_text(json.dumps(themes, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _compact_arrays(value):
    """Keep the existing compact JSON formatting for array values."""
    text = json.dumps(value, indent=4, ensure_ascii=False)
    result = []
    in_array = False
    for char in text:
        if in_array and char in " \n":
            continue
        if in_array and char == ",":
            result.append(", ")
            continue
        if char == "[":
            in_array = True
        elif char == "]":
            in_array = False
        result.append(char)
    return "".join(result)


def main():
    project_dir = Path(__file__).resolve().parent.parent
    apk_file = project_dir / "Forest 专注森林.apk"
    if not apk_file.is_file():
        candidates = sorted(project_dir.glob("*.apk"))
        if len(candidates) == 1:
            apk_file = candidates[0]
        else:
            raise FileNotFoundError("项目根目录需要有一个 APK；多个 APK 时请保留“Forest 专注森林.apk”作为目标文件名。")

    previous_names = _read_previous_names(project_dir)
    trees_dir = project_dir / "docs" / "assets" / "trees"
    trees_dir.mkdir(parents=True, exist_ok=True)

    decoded_dir = project_dir / ".forest-apk-decoded"
    if decoded_dir.resolve().parent != project_dir.resolve():
        raise ValueError("解包目录不能指向工作区外部")
    decoded_dir.mkdir(exist_ok=True)
    # apktool is installed as a Windows .bat file, which must run through cmd.exe.
    subprocess.run(
        ["cmd.exe", "/d", "/c", "apktool.bat", "d", "-f", str(apk_file), "-o", str(decoded_dir)],
        check=True,
        input="",
        text=True,
    )
    drawable_dir = decoded_dir / "res" / "drawable-xxhdpi"
    if not drawable_dir.is_dir():
        raise FileNotFoundError(f"APK 中找不到树图资源目录：{drawable_dir}")

    trees = _discover_trees(drawable_dir, previous_names)
    if not trees:
        raise RuntimeError("APK 中没有发现 tree_type_<数字>_phase_* 树图文件。")

    data = {}
    language_roots = {}
    for language, resource_dir in LANGUAGES.items():
        xml_path = decoded_dir / "res" / resource_dir / "strings.xml"
        if xml_path.exists():
            language_roots[language] = ET.parse(xml_path).getroot()
        else:
            language_roots[language] = None

    for tree_id, tree in sorted(trees.items(), key=lambda item: int(item[0])):
        item = {"nameXML": tree["nameXML"]}
        for language, root in language_roots.items():
            item[f"name{language}"] = _resource_text(root, f"{tree['nameXML']}_title") if root is not None else ""
            description = _resource_text(root, f"{tree['nameXML']}_description") if root is not None else ""
            if description:
                item[f"description{language}"] = description
        item["phase"] = _phase_info(tree["phases"])
        data[tree_id] = item

        _copy_tree_images(tree["files"], trees_dir)

    _remove_replaced_pngs(trees_dir)

    output = project_dir / "docs" / "treeType.json"
    output.write_text(_compact_arrays(data), encoding="utf-8")
    _sync_landscapes(decoded_dir, project_dir)
    if __package__:
        from .serve_forest_web import refresh_snapshots
    else:
        from serve_forest_web import refresh_snapshots
    refresh_snapshots()
    if decoded_dir.resolve().parent != project_dir.resolve():
        raise ValueError("解包目录不能指向工作区外部")
    shutil.rmtree(decoded_dir, ignore_errors=True)
    print(f"已处理 {len(data)} 种树，输出：{output}")
    print(f"树图已直接更新到网页：{trees_dir}")


if __name__ == "__main__":
    main()
