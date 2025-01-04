# TODO: maybe I can add a gui :D?

import os, sys, json, subprocess

# check req libs
required_modules = ["requests", "InquirerPy", "colorama"]


def install_packages(packages):
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} was not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install_packages(required_modules)

import requests
from InquirerPy import prompt
from colorama import Fore, Style, init

init(autoreset=True)


API_BASE_URL = "https://api.modrinth.com/v2"
mods_json_path = "mods.json"
base_download_path = "./mods"


def get_language_choice():
    language_question = {
        "type": "list",
        "name": "language",
        "message": get_message("select_language"),
        "choices": ["en", "tr"],
    }
    answers = prompt([language_question])
    save_language_preference(answers["language"])
    return prompt_user_action()


def load_language_preference():
    if os.path.exists("language.json"):
        with open("language.json", "r") as file:
            return json.load(file).get("language", "en")
    return "en"


def save_language_preference(language):
    with open("language.json", "w") as file:
        json.dump({"language": language}, file)


MESSAGES = {
    "en": {
        "mod_not_found": "No compatible version found for mod {mod_id} with version {minecraft_version} and loader {loader}",
        "mod_fetch_error": "Error: Could not fetch data for mod {mod_id}. Code: {status_code}",
        "mod_downloading": "Downloading mod: {mod_name}",
        "mod_downloaded": "Downloaded: {mod_path}",
        "mod_added": "Added mods: {mod_urls}",
        "mod_already_added": "This mod has already been added.",
        "mod_dependency_downloading": "Downloading dependency {mod_id}...",
        "mod_select_prompt": "Select the mods to add:",
        "json_file_loading_error": "JSON file could not be read: {error}",
        "no_mod_links": "Mod links are empty. Please check 'mods.json'.",
        "versions_load_error": "Could not fetch Minecraft versions or loader information.",
        "minecraft_version_prompt": "Select Minecraft version:",
        "loader_prompt": "Select loader (mod loader):",
        "compatible_version_found": "Compatible version found: {version_number}",
        "downloading_file": "Downloading: {file_name}",
        "download_error_file": "Error: {file_name} could not be downloaded.",
        "action_prompt": "What would you like to do?",
        "select_language": "Select Language:",
        "set_language": "Change Language",
        "download_mods": "Download Added Mods",
        "add_mods": "Add New Mods",
        "search_mods": "Search mods on Modrinth:",
        "search_query_empty": "Search query cannot be empty. Please enter something.",
        "search_no_mods_found": "No mods found for the given search query.",
        "back_to_main_menu": "Back to Main Menu",
        "what_would_you_like_to_do_next": "What would you like to do next?",
        "add_another_mod": "Add another mod",
        "exit": "Exit",
        "goodbye": "GoodBye ^^",
    },
    "tr": {
        "mod_not_found": "{mod_id} için {minecraft_version} ve {loader} uyumlu sürüm bulunamadı",
        "mod_fetch_error": "{mod_id} için veri alınamadı. Kod: {status_code}",
        "mod_downloading": "Mod indiriliyor: {mod_name}",
        "mod_downloaded": "İndirildi: {mod_path}",
        "mod_added": "Eklenen modlar: {mod_urls}",
        "mod_already_added": "Bu mod zaten eklenmiş.",
        "mod_select_prompt": "Eklenecek modu seçin",
        "mod_dependency_downloading": "Bağımlılık {mod_id} indiriliyor...",
        "json_file_loading_error": "JSON dosyası okunamadı: {error}",
        "no_mod_links": "Mod bağlantıları boş. Lütfen 'mods.json' dosyasını kontrol edin.",
        "versions_load_error": "Minecraft sürümleri veya loader bilgileri alınamadı.",
        "minecraft_version_prompt": "Minecraft sürümünü seçin:",
        "loader_prompt": "Loader (mod yükleyici) seçin:",
        "compatible_version_found": "Uyumlu sürüm bulundu: {version_number}",
        "downloading_file": "İndiriliyor: {file_name}",
        "download_error_file": "Hata: {file_name} indirilemedi.",
        "action_prompt": "Ne yapmak istersiniz?",
        "select_language": "Dil Seçin:",
        "set_language": "Dili Değiştir",
        "download_mods": "Eklenmiş Modları İndir",
        "add_mods": "Yeni Mod Ekle",
        "search_mods": "Modrinth'te mod ara:",
        "search_query_empty": "Arama sorgusu boş olamaz. Lütfen bir şeyler girin.",
        "search_no_mods_found": "Verilen arama sorgusu için mod bulunamadı.",
        "back_to_main_menu": "Ana Menüye Dön",
        "what_would_you_like_to_do_next": "Bundan sonra ne yapmak istersiniz?",
        "add_another_mod": "Başka Mod Ekle",
        "exit": "Çıkış",
        "goodbye": "Görüşürüz ^^",
    },
}


def get_message(key, **kwargs):
    language = load_language_preference()
    message = MESSAGES[language].get(key, key)
    return message.format(**kwargs)


def load_mod_links(file_path):
    try:
        if not os.path.exists(file_path):

            with open(file_path, "w") as f:
                json.dump({"mods": []}, f, indent=4)
            return []
        else:
            with open(file_path, "r") as f:
                data = json.load(f)
                return data.get("mods", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(get_message("json_file_loading_error", error=e))
        return []


def extract_mod_id(mod_url):
    return mod_url.rstrip("/").split("/")[-1]


def download_mods():
    mod_links = load_mod_links(mods_json_path)
    if not mod_links:
        print(get_message("no_mod_links"))
        return

    response_versions = requests.get(f"{API_BASE_URL}/tag/game_version")
    response_loaders = requests.get(f"{API_BASE_URL}/tag/loader")
    if response_versions.status_code != 200 or response_loaders.status_code != 200:
        print(get_message("versions_load_error"))
        return

    minecraft_versions = [
        v["version"]
        for v in response_versions.json()
        if not v["version"].startswith("old_")
    ]
    loaders = [l["name"] for l in response_loaders.json()]
    version, loader = get_user_minecraft_choices(minecraft_versions, loaders)

    for link in mod_links:
        mod_id = extract_mod_id(link)
        download_mod_files(mod_id, version, loader, base_download_path)

    next_action = prompt(
        {
            "type": "list",
            "name": "next_action",
            "message": get_message("what_would_you_like_to_do_next"),
            "choices": [
                {"name": get_message("back_to_main_menu"), "value": "main_menu"},
                {"name": get_message("exit"), "value": "exit"},
            ],
        }
    )["next_action"]

    if next_action == "main_menu":
        prompt_user_action()
    else:
        print(Fore.YELLOW + get_message("goodbye"))


def download_mod_files(
    mod_id, minecraft_version, loader, base_download_path, visited_mods=None
):
    if visited_mods is None:
        visited_mods = set()

    if mod_id in visited_mods:
        return
    visited_mods.add(mod_id)

    print(get_message("mod_downloading", mod_name=mod_id))
    response = requests.get(f"{API_BASE_URL}/project/{mod_id}/version")
    if response.status_code != 200:
        print(
            get_message(
                "mod_fetch_error", mod_id=mod_id, status_code=response.status_code
            )
        )
        return

    versions = response.json()
    for version in versions:
        if (
            minecraft_version in version["game_versions"]
            and loader in version["loaders"]
        ):
            print(
                get_message(
                    "compatible_version_found", version_number=version["version_number"]
                )
            )
            loader_path = os.path.join(base_download_path, loader)
            version_path = os.path.join(loader_path, minecraft_version)
            os.makedirs(version_path, exist_ok=True)

            for file in version["files"]:
                if file["primary"]:
                    file_url = file["url"]
                    file_name = file["filename"]
                    file_path = os.path.join(version_path, file_name)

                    print(get_message("downloading_file", file_name=file_name))
                    file_response = requests.get(file_url)
                    if file_response.status_code == 200:
                        with open(file_path, "wb") as f:
                            f.write(file_response.content)
                        print(get_message("mod_downloaded", mod_path=file_path))
                    else:
                        print(get_message("download_error_file", file_name=file_name))

            if "dependencies" in version:
                for dep in version["dependencies"]:
                    dep_mod_id = dep["project_id"]
                    print(get_message("mod_dependency_downloading", mod_id=dep_mod_id))
                    download_mod_files(
                        dep_mod_id,
                        minecraft_version,
                        loader,
                        base_download_path,
                        visited_mods,
                    )
            return
    print(
        get_message(
            "mod_not_found",
            mod_id=mod_id,
            minecraft_version=minecraft_version,
            loader=loader,
        )
    )


def get_user_minecraft_choices(versions, loaders):
    version_question = {
        "type": "list",
        "name": "version",
        "message": get_message("minecraft_version_prompt"),
        "choices": versions,
    }
    loader_question = {
        "type": "list",
        "name": "loader",
        "message": get_message("loader_prompt"),
        "choices": loaders,
    }
    answers = prompt([version_question, loader_question])
    version = answers["version"]
    loader = answers["loader"]
    return version, loader


def search_modrinth(query):
    if not query.strip():
        return []

    response = requests.get(f"{API_BASE_URL}/search", params={"query": query})
    if response.status_code != 200:
        print(
            get_message(
                "mod_fetch_error", mod_id=query, status_code=response.status_code
            )
        )
        return []

    mods = response.json().get("hits", [])

    return mods


def add_mods_to_json():
    mod_links = load_mod_links(mods_json_path)

    search_query = prompt(
        {
            "type": "input",
            "name": "search_query",
            "message": get_message("search_mods"),
        }
    )["search_query"]

    if not search_query.strip():
        return prompt_user_action("search_query_empty", "yellow")

    search_results = search_modrinth(search_query)
    if not search_results:
        return prompt_user_action("search_no_mods_found", "red")

    mod_choices = [
        {"name": mod["title"], "value": mod["slug"]} for mod in search_results
    ]

    mod_question = {
        "type": "list",
        "name": "selected_mod",
        "message": get_message("mod_select_prompt"),
        "choices": mod_choices,
    }

    selected_mod = prompt([mod_question])["selected_mod"]

    mod_url = f"https://modrinth.com/mod/{selected_mod}"

    if mod_url in mod_links:
        return prompt_user_action("mod_already_added", "yellow")

    mod_links.append(mod_url)

    with open("mods.json", "w") as f:
        json.dump({"mods": mod_links}, f, indent=4)

    print(get_message("mod_added", mod_urls=[mod_url]))

    next_action = prompt(
        {
            "type": "list",
            "name": "next_action",
            "message": get_message("what_would_you_like_to_do_next"),
            "choices": [
                {"name": get_message("add_another_mod"), "value": "add_mod"},
                {"name": get_message("back_to_main_menu"), "value": "main_menu"},
                {"name": get_message("exit"), "value": "exit"},
            ],
        }
    )["next_action"]

    if next_action == "add_mod":
        add_mods_to_json()
    elif next_action == "main_menu":
        prompt_user_action()
    else:
        print(Fore.YELLOW + get_message("goodbye"))


def prompt_user_action(message=None, message_color=None):
    os.system("cls")
    if message is not None:
        if message_color is not None:
            print(
                getattr(Fore, message_color.upper(), Fore.WHITE) + get_message(message)
            )
        else:
            print(get_message(message))

    action_question = {
        "type": "list",
        "name": "action",
        "message": get_message("action_prompt"),
        "choices": [
            get_message("set_language"),
            get_message("add_mods"),
            get_message("download_mods"),
            get_message("exit"),
        ],
    }
    action = prompt([action_question])["action"]

    if action == get_message("set_language"):
        get_language_choice()
    elif action == get_message("download_mods"):
        download_mods()
    elif action == get_message("add_mods"):
        add_mods_to_json()
    else:
        print(Fore.YELLOW + get_message("goodbye"))


if not os.path.exists("language.json"):
    get_language_choice()


prompt_user_action()
