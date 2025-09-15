# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

EasyDev is a simplified and enhanced iOS jailbreak development framework based on MonkeyDev. It provides Xcode project templates for creating iOS tweaks, command-line tools, and app plugins that work with both rootfull and rootless jailbreaks.

## Architecture

### Core Components

- **Templates System**: Xcode project templates for different project types
  - CaptainHook/Logos Tweaks for iOS app hooking
  - Command-line tools for iOS devices
  - App plugins and XPC services
  - PreferenceLoader bundles for Settings integration
  
- **Build System**: Integrates with theos build system and provides custom build scripts
  - `pack-ios.sh` handles app packaging and dylib injection
  - Supports both rootfull and rootless jailbreak environments
  - Automatic code signing and framework handling

- **Tools Collection**: Pre-compiled tools for iOS development and reverse engineering
  - Located in `bin/` and `tools/` directories
  - Includes class-dump, frida tools, LLDB extensions, and more

### Key Directories

- `templates/` - Xcode project templates (.xctemplate bundles)
- `bin/` - Pre-compiled development tools and install scripts
- `tools/` - Additional development tools as git submodules
- `lib/` - Dynamic libraries including dumpdecrypted.dylib and frida-gadget

## Installation & Setup

### Prerequisites
- Xcode 10-15 supported
- theos framework installed at `/opt/theos`
- ldid installed via Homebrew: `brew install ldid`

### Installation Commands
```bash
# Install EasyDev framework
sudo git clone --recursive https://github.com/lemon4ex/EasyDev.git /opt/EasyDev

# Install to Xcode
cd /opt/EasyDev/bin
chmod +x ed-install
./ed-install
```

### Uninstallation
```bash
cd /opt/EasyDev/bin
chmod +x ed-uninstall
./ed-uninstall
```

## Development Workflow

### Creating New Projects
1. Open Xcode and create new project
2. Select EasyDev templates under "Project Templates"
3. Choose project type:
   - **CaptainHook/Logos Tweak**: For hooking iOS applications
   - **iOS Command-line Tool**: For creating CLI tools
   - **iOS App Plugin**: For creating app extensions
   - **Debian Command-line Tool**: For system-level tools

### Build Configuration
- Projects automatically configure build settings for iOS development
- Support for both rootfull (`/usr/lib`) and rootless (`/var/jb/usr/lib`) environments
- Custom build phases handle dylib injection and app packaging

### Testing & Deployment
- Built artifacts placed in `LatestBuild/` symlink
- Automatic IPA creation for app plugins
- SSH deployment to jailbroken devices (configure `EasyDevDeviceIP` environment variable)

## Common Development Tasks

### Building Projects
Projects use standard Xcode build system with custom build phases:
```bash
# Build from command line (if using xcodebuild)
xcodebuild -project MyProject.xcodeproj -scheme MyProject -configuration Debug
```

### Working with Tweaks
- **CaptainHook**: C++-based hooking framework
- **Logos**: Preprocessor-based hooking syntax
- Both support method swizzling and class manipulation

### Debugging
- Use included LLDB scripts in `tools/LLDB/` and `tools/xia0LLDB/`
- frida-ios-dump for decrypting App Store binaries
- class-dump for generating headers

### Environment Variables
Set in shell profile (automatically configured during installation):
- `EasyDevPath=/opt/EasyDev` - Framework installation path
- `EasyDevDeviceIP=` - Target device IP for deployment
- `PATH` includes `/opt/EasyDev/bin` for tool access

## Project Types & Templates

### Tweak Development
- **CaptainHook Tweak**: Advanced C++ hooking with method signatures
- **Logos Tweak**: Simplified syntax with preprocessing
- Both generate `.dylib` files for injection into target applications

### Command-line Tools
- **iOS Command-line Tool**: Runs on iOS devices, minimal template
- **Debian Command-line Tool**: Full debian package with postinst scripts

### App Development
- **iOS App Plugin**: Complete app template with target app integration
- **Cocoa Touch Library**: Reusable library components
- **PreferenceLoader Bundle**: Settings panel extensions

## Tool Integration

The framework includes numerous reverse engineering and development tools:
- **frida-ios-dump**: App decryption and dumping
- **class-dump**: Objective-C header generation  
- **optool**: Mach-O binary manipulation
- **jtool/jtool2**: Advanced binary analysis
- **restore-symbol**: Symbol restoration for stripped binaries

Access tools directly from command line after installation (added to PATH).

## Jailbreak Environment Support

### Rootfull Jailbreaks (Traditional)
- Libraries installed to `/usr/lib/`
- Full filesystem access
- Compatible with older jailbreak tools

### Rootless Jailbreaks (Modern) 
- Libraries installed to `/var/jb/usr/lib/`
- Sandboxed environment with restricted filesystem access
- Required for iOS 15+ jailbreaks

Templates automatically configure appropriate paths based on target environment selection during project creation.