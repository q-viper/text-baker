# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2026-02-17

### Added
- Character segmentation dialog: improved UI layout for easier use
- Checkbox to invert color before saving cropped region
- Info label and documentation updated to mention invert option
- Save logic respects invert checkbox

### Improved
- Button layout and usability in segmentation dialog
- Documentation in `docs/character-segmentation.md` for new features

### Fixed
- Lint error (SIM102): Use a single `if` statement instead of nested `if` in `mouse_release`

### References
- [#1 Config is not being used properly.](https://github.com/q-viper/text-baker/issues/1)
- [#2 Backgrounds and textures are not being used properly.](https://github.com/q-viper/text-baker/issues/2)
- [#3 Transformation is still not clearly followed from last generation.](https://github.com/q-viper/text-baker/issues/3)
- [#4 Have a feature in UI to segment the character.](https://github.com/q-viper/text-baker/issues/4)

## [0.1.4] - 2026-02-15

### Added
- **Drawing Canvas Feature**: Built-in character drawing tool with professional UI
  - Draw custom characters directly in the application
  - Real-time drawing with pen and eraser tools
  - Adjustable pen width (1-50px) with mouse wheel support
  - Custom color picker for pen and background
  - Crosshair cursor for precise drawing, pointing hand for eraser
  - Delete key shortcut to clear canvas
  - Canvas empty detection with improved sensitivity
  
- **Async Save with Progress Feedback**
  - Non-blocking save using background thread (`SaveWorker`)
  - Animated progress bar during save operation
  - Success confirmation message with auto-hide (3 seconds)
  - No UI freezing during character save
  
- **Incremental Dataset Updates**
  - Smart dataset updating - only adds new characters instead of full rescan
  - 100x faster character addition to the list
  - Maintains sorted character list automatically
  
- **Custom Character Management**
  - Characters saved to `.textbaker/custom_characters/` in working directory
  - Automatic file numbering (`drawn_0001.png`, `drawn_0002.png`, etc.)
  - Immediate integration with main dataset
  - 512x512px PNG format for high quality

### Improved
- Canvas empty detection now uses:
  - 16px sampling step (was 32px) for better coverage
  - Lower threshold (10 vs 15) for improved sensitivity
  - Immediate return on first non-background pixel found
  
- UI Responsiveness
  - All blocking operations removed
  - Progress indicators for long-running tasks
  - Visual feedback instead of modal dialogs for validation errors

### Fixed
- Drawing window no longer freezes during character save
- "Draw something first" false positive detections
- Dataset list updates without full directory rescan
- Red border error indicator resets after successful save
- Window title error message resets after successful save

### Documentation
- Added comprehensive drawing canvas guide (`docs/guide/custom-characters.md`)
- Updated README with drawing feature
- Created technical fix documentation (`DRAWING_WINDOW_FIX.md`, `FINAL_FREEZE_FIX.md`)

## [0.1.3] - 2026-02-14

### Added
- Initial public release preparations
- PyPI compatibility improvements

## [0.1.2] - 2026-02-13

### Added
- Documentation improvements
- Example images for README

## [0.1.1] - 2026-02-12

### Added
- Initial release
- GUI application
- CLI tool
- Core text generation features
- Transformation capabilities
- Texture and background support
