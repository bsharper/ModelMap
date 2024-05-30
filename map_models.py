import os
import sys
import json
import platform

def get_ollama_model_path():
    # Check if OLLAMA_MODELS environment variable is set
    env_model_path = os.environ.get('OLLAMA_MODELS')
    if env_model_path:
        return env_model_path

    # Determine the model path based on the operating system
    system = platform.system()
    if system == 'Darwin':  # macOS
        return os.path.join(os.path.expanduser('~'), '.ollama', 'models')
    elif system == 'Linux':
        return '/usr/share/ollama/.ollama/models'
    elif system == 'Windows':
        return os.path.join(os.environ['USERPROFILE'], '.ollama', 'models')
    else:
        raise Exception('Unsupported Operating System')


def extract_digests(json_record):
    result = {}
    for layer in json_record.get('layers', []):
        media_type = layer.get('mediaType')
        digest = layer.get('digest')
        if media_type == "application/vnd.ollama.image.model":
            result['gguf'] = digest
        elif media_type == "application/vnd.ollama.image.projector":
            result['mmproj'] = digest
    return result

def is_likely_json(filepath):
    try:
        with open(filepath, 'r') as file:
            first_char = file.read(1).strip()
            if first_char in ('{', '['):
                file.seek(0)
                j = json.load(file)
                return True
        return False
    except Exception:
        return False


def search_for_models(directory):
    models = {}
    models_map = {}
    blobs = {}
    is_windows = platform.system() == "Windows"
    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            sz = os.path.getsize(full_path)
            print (f"{sz} {full_path}")
            if root.endswith("blobs"):
                blobs[file.replace("sha256-", "sha256:")] = full_path
            #if (file == "latest" or ("registry.ollama.ai" in full_path and "library" in full_path)) and sz < 2048: 
            if sz < 2048 and is_likely_json(full_path):
                els = full_path.split(os.sep)
                model_name = f"{els[-2]}-{els[-1]}"
                j = json.load(open(full_path))
                models[model_name] = extract_digests(j)
    for model_name in models.keys():
        model = models[model_name]
        obj = model
        try:
            obj = {x: blobs[model[x]] for x in model.keys()}
        except KeyError as ex:
            print (ex)
            print ("This likely means that a manifest is pointing to a file that does not exist")
        
        models_map[model_name] = obj
    return models_map

def generate_link_pairs(models_map, target_path=""):
    if target_path:
        target_path = os.path.expanduser(target_path)
    links = []
    for model_name in models_map:
        model = models_map[model_name]
        for file_type in model:
            file_path = model[file_type]
            filename = f"{model_name}.{file_type}"
            if target_path:
                filename = os.path.join(target_path, filename)
            links.append({'target': file_path, 'linkpath': filename})
    return links

def print_link_script(links):
    is_windows = platform.system() == "Windows"
    for link in links:
        if is_windows:
            print (f"mklink '{link['linkpath']}' '{link['target']}'")
        else:
            print (f"ln -s '{link['target']}' '{link['linkpath']}'")

def create_links(links):
    for link in links:
        linkpath = link['linkpath']
        target = link['target']
        print (f'Creating link "{linkpath}" => "{target}"')
        if os.path.exists(link['linkpath']) or os.path.islink(link['linkpath']):
            os.unlink(linkpath)
        os.symlink(link['target'], link['linkpath'])


def header(ollama_path, link_path=""):
    width = 60
    print ("="*width)
    print (f"Ollama models path : {ollama_path}")
    if link_path:
        link_path = os.path.expanduser(link_path)
        print (f"Link path          : {link_path}")
    print ("="*width)


if __name__ == "__main__":
    args = sys.argv[1:]
    link_path=""
    if len(args) > 0:
        if args[0] == "-h" or args[0] == "--help":
            bn = os.path.basename(sys.argv[0])
            print (f"Usage: python {bn} ../some_path")
            print ("")
            print ("Creates symbolic links to the models downloaded by ollama")
            print ("Run without any arguments to see the models it will process")
            sys.exit(0)
        link_path = args[0]
        if not os.path.exists(link_path):
            print ('Error: provided path "{link_path}" does not exist')
    ollama_path = get_ollama_model_path()
    header(ollama_path, link_path)
    models_map = search_for_models(ollama_path)
    links = generate_link_pairs(models_map, link_path)
    if link_path:
        create_links(links)
    else:
        print_link_script(links)
