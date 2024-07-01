# Makefile to clean the directory of generated files

# List of generated files to be cleaned
GENERATED_FILES = route_animation.gif route_animation_map.html route_animation.mp4 route.html route_with_animation.html route_animation_moving_map.mp4 thumbnail.png

# Default target
all:
	@echo "Usage: make clean"

# Clean target to remove generated files
clean:
	rm -f $(GENERATED_FILES)
	@echo "Cleaned up generated files."

.PHONY: all clean
