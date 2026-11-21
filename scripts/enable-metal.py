#!/usr/bin/env python3
"""Apply the small macOS-only CMake changes needed by this overlay."""

from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: enable-metal.py path/to/CMakeLists.txt")

path = Path(sys.argv[1])
text = path.read_text()
old_backend = '''if(ILS_BACKEND STREQUAL "CUDA")
    set(GGML_CUDA   ON  CACHE BOOL "" FORCE)
    set(GGML_VULKAN OFF CACHE BOOL "" FORCE)
elseif(ILS_BACKEND STREQUAL "VULKAN")
    set(GGML_CUDA   OFF CACHE BOOL "" FORCE)
    set(GGML_VULKAN ON  CACHE BOOL "" FORCE)
else()
    message(FATAL_ERROR "ILS_BACKEND must be CUDA or VULKAN, not '${ILS_BACKEND}'")
endif()'''
new_backend = '''if(ILS_BACKEND STREQUAL "CUDA")
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
old_zlib = '''if(NOT WIN32)
    set(ZLIB_USE_STATIC_LIBS ON)  # libz.a: one dependency less at run time
endif()'''
new_zlib = '''if(NOT WIN32 AND NOT APPLE)
    set(ZLIB_USE_STATIC_LIBS ON)  # libz.a: one dependency less at run time
endif()'''

changed = False
if new_backend in text:
    print(f"Metal backend already enabled in {path}")
elif old_backend in text:
    text = text.replace(old_backend, new_backend, 1)
    changed = True
else:
    raise SystemExit(
        f"Could not find the expected backend configuration in {path}; "
        "upstream may have changed. No file was modified."
    )

if new_zlib in text:
    print("macOS zlib static-link workaround already applied")
elif old_zlib in text:
    text = text.replace(old_zlib, new_zlib, 1)
    changed = True
else:
    raise SystemExit(
        f"Could not find the expected zlib configuration in {path}; "
        "upstream may have changed. No file was modified."
    )

if changed:
    path.write_text(text)
    print(f"Applied macOS CMake changes in {path}")
