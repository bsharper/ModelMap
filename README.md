
**map_models.py**
=====================


`map_models.py` is a Python script that creates sensible symbolic links to Ollama models. Ollama stores files by sha256 hash. With this script instead of remembering `/usr/share/ollama/.ollama/models/blobs/sha256-4fed7364ee3e0c7cb4fe0880148bfdfcd1b630981efa0802a6b62ee52e7da97e` you can just remember `ollama/phi3-latest.gguf`.

The script searches for models in the OLLAMA_MODELS path (if that environment variable is set) or a default path based on the operating system. If provided a path as an argument, the script will create a symbolic link for each model in that path, making it easier to use ollama models in with other programs (like the excellent llama.cpp).


**Usage**
-----

`python map_models.py [link_path]`

* `[link_path]` is an optional argument specifying the path where the symbolic links will be created. If not provided, the script will only print the commands you can run to link the models.

For example:

```
python map_models.py llama.cpp/ollama
```

This would create symbolic links to the Ollama models in `./llama.cpp/ollama`.

This script is hacky and isn't as robust as it could be, but it works great for me so I thought I'd share it.