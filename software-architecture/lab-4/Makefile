BUILD_DIR := build
TARGET    := proxy_image_editor

.PHONY: all configure build run clean

all: build

configure:
	@cmake -S . -B $(BUILD_DIR) -DCMAKE_BUILD_TYPE=Release

build: configure
	@cmake --build $(BUILD_DIR) --parallel

run: build
	@./$(BUILD_DIR)/$(TARGET)

clean:
	@rm -rf $(BUILD_DIR)
