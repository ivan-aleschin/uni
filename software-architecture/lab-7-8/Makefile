.PHONY: all build run clean restore

# Если direnv активен — pkg-config найдёт raylib сам.
# Если direnv не активен (например, прямой запуск через CI) —
# вторая попытка через `nix develop` из корня репозитория.
REPO_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null)
RAYLIB_LIBDIR := $(shell pkg-config --variable=libdir raylib 2>/dev/null)
ifeq ($(RAYLIB_LIBDIR),)
RAYLIB_LIBDIR := $(shell nix develop $(REPO_ROOT) --command pkg-config --variable=libdir raylib 2>/dev/null)
endif

DOTNET_CLI_HOME ?= /tmp/.dotnet
export DOTNET_CLI_HOME

OUT := bin/Debug/net8.0
BUNDLED_NATIVE := $(OUT)/runtimes/linux-x64/native/libraylib.so

all: build

restore:
	@dotnet restore

build: restore
	@dotnet build --nologo -v q
	@# Bundled libraylib.so из NuGet не запустится на NixOS — удаляем.
	@rm -f $(BUNDLED_NATIVE)

run: build
	@LD_LIBRARY_PATH=$(RAYLIB_LIBDIR):$$LD_LIBRARY_PATH dotnet run --no-build

clean:
	@rm -rf bin obj
