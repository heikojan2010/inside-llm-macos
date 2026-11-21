#!/usr/bin/env python3
"""Enable the upstream CMake project's llama.cpp Metal backend."""

from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: enable-metal.py path/to/CMakeLists.txt")

path = Path(sys.argv[1])
text = path.read_text()
old = '''if(ILS_BACKEND STREQUAL "CUDA")
    set(GGML_CUDA   ON  CACHE BOOL "" FORCE)
    set(GGML_VULKAN OFF CACHE BOOL "" FORCE)
elseif(ILS_BACKEND STREQUAL "VULKAN")
    set(GGML_CUDA   OFF CACHE BOOL "" FORCE)
    set(GGML_VULKAN ON  CACHE BOOL "" FORCE)
else()
    message(FATAL_ERROR "ILS_BACKEND must be CUDA or VULKAN, not '${ILS_BACKEND}'")
endif()'''
new = '''if(ILS_BACKEND STREQUAL "CUDA")
    set(GGML_CUDA   ON  CACHE BOOL "" FORCE)
    set(GGML_VULKAN OFF CACHE BOOL "" FORCE)
    set(GGML_METAL  OFF CACHE BOOL "" FORCE)
elseif(ILS_BACKEND STREQUAL "VULKAN")
    set(GGML_CUDA   OFF CACHE BOOL "" FORCE)
    set(GGML_VULKAN ON  CACHE BOOL "" FORCE)
    set(GGML_METAL  OFF CACHE BOOL "" FORCE)
elseif(ILS_BACKEND STREQUAL "METAL")
    if(NOT APPLE)
        message(FATAL_ERROR "ILS_BACKEND=METAL requires macOS")
    endif()
    set(GGML_CUDA   OFF CACHE BOOL "" FORCE)
    set(GGML_VULKAN OFF CACHE BOOL "" FORCE)
    set(GGML_METAL  ON  CACHE BOOL "" FORCE)
else()
    message(FATAL_ERROR "ILS_BACKEND must be CUDA, VULKAN, or METAL, not '${ILS_BACKEND}'")
endif()'''

if new in text:
    print(f"Metal backend already enabled in {path}")
elif old in text:
    path.write_text(text.replace(old, new, 1))
    print(f"Enabled Metal backend in {path}")
else:
    raise SystemExit(
        f"Could not find the expected backend configuration in {path}; "
        "upstream may have changed. No file was modified."
    )
