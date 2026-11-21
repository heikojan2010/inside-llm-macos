# inside-llm for Apple Silicon

A native macOS build overlay for [inside-llm](https://github.com/manuelgscom/inside-llm), configured for Apple Silicon Macs such as the Mac mini M4. It builds the upstream app natively (no Docker) and enables llama.cpp's Metal backend plus architecture-native CPU optimizations.

> This repository is currently a standalone overlay, not a GitHub fork containing the upstream source. The build script fetches upstream recursively and applies the small Metal-backend change locally before building.

## Build on a Mac mini M4

Install Xcode Command Line Tools and the build dependencies:

```sh
xcode-select --install
brew install cmake ninja node
```

Then build:

```sh
git clone https://github.com/heikojan2010/inside-llm-macos.git
cd inside-llm-macos
./scripts/build-macos.sh
```

The script checks out the upstream repository and llama.cpp submodule into `build/upstream`, builds the Svelte web app, and compiles the engine for `arm64` with Metal enabled and `GGML_NATIVE=ON`. The resulting executable is `build/upstream/build/macos/inside-llm`.

Run it with the model picker:

```sh
./scripts/run-macos.sh
```

Or compare two GGUF files:

```sh
./scripts/run-macos.sh -a /path/to/model-Q4_K_M.gguf -b /path/to/model-Q8_0.gguf
```

Models are downloaded/stored in the current working directory's `models` folder by default. Keep model files and context sizes within the unified-memory capacity of your Mac; running two models at once requires room for both models and their context/KV caches.

## Rebuild after upstream changes

The checkout is retained in `build/upstream`. Update it and rebuild with:

```sh
git -C build/upstream pull --recurse-submodules
git -C build/upstream submodule update --init --recursive
./scripts/build-macos.sh
```

The local patcher is idempotent. It only changes the upstream top-level `CMakeLists.txt` in the generated checkout; it does not change this overlay repository's files.

## What is optimized

- **Metal GPU acceleration:** llama.cpp's Metal backend offloads supported inference work to the Apple GPU and uses unified memory.
- **Apple Silicon CPU tuning:** `GGML_NATIVE=ON` lets the compiler and ggml use the build host's supported CPU features. Build on the M4 itself for M4-specific tuning; the binary may not be portable to older Macs.
- **Native build:** CMake, Ninja, Node.js, and Xcode tools run directly on macOS, avoiding Linux containers and CUDA/Vulkan assumptions.

This is a build/configuration port, not a claim that every workload will run entirely on the GPU. llama.cpp may use CPU operations for unsupported kernels, and actual speed depends on model, quantization, context length, and memory pressure.

## Troubleshooting

- If CMake cannot find Metal tools, install/update Xcode Command Line Tools and accept the Xcode license.
- If CMake reports `Could NOT find ZLIB (missing: ZLIB_LIBRARY)`, the upstream build is forcing static zlib. The macOS patcher now leaves zlib dynamic so CMake can use the system library. Remove the stale configure cache and retry: `rm -rf build/upstream/build/macos` followed by `./scripts/build-macos.sh`.
- If upstream's CMake configuration changes, the patch script intentionally stops rather than silently making a potentially incorrect edit.
- For a clean rebuild, remove `build/upstream` and run `./scripts/build-macos.sh` again.

Upstream project and license: [manuelgscom/inside-llm](https://github.com/manuelgscom/inside-llm).