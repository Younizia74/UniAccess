# UniAccess

[![CI/CD](https://github.com/Younizia74/UniAccess/workflows/CI/CD/badge.svg)](https://github.com/Younizia74/UniAccess/actions)
[![License: MIT OR Apache-2.0](https://img.shields.io/badge/License-MIT%20OR%20Apache--2.0-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Accessibility](https://img.shields.io/badge/Accessibility-Enabled-green.svg)](https://github.com/Younizia74/UniAccess)

## 🚀 **Technical Leadership Opportunity!**

**We're looking for developers passionate about accessibility to take technical leadership of this project!**

This universal accessibility project was created with a clear vision but the creator recognizes their technical limitations. If you're an experienced developer passionate about accessibility, we invite you to:

- **Take technical leadership** of the project
- **Improve architecture** and best practices  
- **Guide the community** of contributors
- **Evolve the project** according to your expertise

**Why join this project?**
- Significant impact on digital accessibility
- Recognition in the open source community
- Technical freedom to innovate
- Project with solid foundation already established

**How to get started?**
- Check our [contribution guide](CONTRIBUTING.md#technical-leadership-and-responsibility)
- Create an issue with the `leadership` label
- Present your vision and action plan

---

This project aims to provide a universal accessibility solution (e.g., speech synthesis, braille display, haptic feedback, spatial audio, AI and image recognition, etc.) on Linux (and eventually on Android and Windows) to facilitate the use of applications (e.g., LibreOffice, editors, Android applications, etc.) by users with disabilities.

## Features

- **Speech synthesis** (via the speech_backend module): read information aloud (texts, notifications, etc.).
- **Braille display** (via the braille module): translate text into braille (e.g., via BRLTTY).
- **Haptic feedback** (via the haptics module): provide tactile feedback (vibrations, tactile feedback) to reinforce interaction.
- **Spatial audio** (via the audio_spatial module): render 3D sounds (spatialization) to indicate the position of an element in space.
- **AI and image recognition** (via the ai module): analyze and describe the environment (e.g., describe an image or interface) using OCR, object recognition, etc.
- **Input management** (via the input_listener module): intercept inputs (keyboard, mouse) and transmit them to the AT-SPI backend to communicate with applications.
- **AT-SPI backend** (via the atspi_backend module): communicate with applications (e.g., LibreOffice, editors, Android applications) to retrieve information (texts, elements, states, etc.).
- **Configuration and accessibility** (via the config, accessibility modules): customize behavior (contrast, shortcuts, magnifier, etc.) to adapt to the environment (Linux, Android, Windows).

## Installation

See the [installation guide](docs/guide_installation.md) for detailed steps (e.g., install dependencies, clone repository, run tests, launch application, etc.).

## Documentation

- [Architecture diagram](docs/architecture.md): details the diagram and interactions between modules (e.g., user interface, input_listener, speech_backend, braille, haptics, audio_spatial, ai, atspi_backend, config, accessibility, etc.).
- [Advanced usage guide](docs/guide_avance.md): explains how to use advanced features (contrast, shortcuts, braille, haptic feedback, spatial audio, AI, speech synthesis, etc.).
- [Internal API documentation](docs/api.md): details the functions, classes and parameters of modules to facilitate integration and extension of the project.
- [Code examples](docs/examples.md): shows how to use these APIs in concrete cases (e.g., calculate contrast, record a shortcut, display text in braille, trigger vibration, play spatial sound, recognize objects, read text, etc.).
- [Contribution guide](docs/contributing.md): details the steps (clone repository, install dependencies, run tests, submit pull request, etc.) so other developers can contribute to the project.

## Continuous Integration

The project integrates a continuous integration (CI) workflow (in [.github/workflows/ci.yml](.github/workflows/ci.yml)) that automatically runs tests (unit, integration, accessibility) on each push (or pull request) to the main branch (via GitHub Actions).

## Build System

The project integrates a Makefile (in the root directory) that defines targets (install, test, package, clean) to facilitate the setup of the build system (e.g., install dependencies, run tests, generate package, clean generated files).

## About the Creator

**Important:** I am not a professional developer, but I have a clear vision of what this project can bring to the accessibility community. I discovered Cursor and AI which allowed me to create this foundation, but I recognize my technical limitations.

**My vision:** Make the digital world accessible to everyone, regardless of disabilities. This project aims to combine AI, multimodality (voice, braille, haptic, spatial audio) and universal accessibility.

**My role:** I remain open to suggestions, improvements and letting competent developers take technical direction of the project. My goal is for this project to serve the community, even if it means entrusting it to more experienced hands.

**Why this transparency?** I prefer to be honest about my skills and expectations. If you are a developer and this project interests you, don't hesitate to contribute or even take a technical leadership role.

## Contribution

See the [contribution guide](docs/contributing.md) for detailed steps (clone repository, install dependencies, run tests, submit pull request, etc.) so other developers can contribute to the project.

## Improvement Idea (Semi-autonomous AI)

In the long term, we plan to integrate an AI (e.g., via a bot or service) that learns (e.g., via machine learning or reinforcement learning) from contributions (e.g., commits, PRs, reviews, etc.) to help (e.g., by suggesting improvements, detecting bugs, generating tests, updating documentation, etc.) developers and, ultimately, improve the project semi-autonomously. This approach (e.g., by analyzing commits, PRs, reviews, etc. and proposing suggestions) could, in the long term, facilitate maintenance and increase project compatibility.

## License

This project is under **MIT** AND **Apache 2.0** license (dual license). You can choose the license that suits you best:

- [MIT License](LICENSE) - Simple and permissive
- [Apache 2.0 License](LICENSE-APACHE) - With patent protection

This dual approach offers maximum flexibility to users and contributors.

# UniAccess – Universal Accessibility

## Objective
This project aims to make the digital world accessible to everyone, on Linux, Windows, Android, gaming consoles, and more. It brings together modules for accessibility management (voice, braille, haptic, AI, etc.), application integration, and centralized configuration.

## Project Structure

```
uniaccess/
  core/ ...
  apps/ ...
  ...
uniaccess_android/
  apps/
    system/
    user/
    accessibility/
    input_method/
    notification/
    widget/
    service/
    content/
console/
haptics/
spatial_audio/
braille/
models/
docs/
```

## Main Modules
- **Linux/Windows**: accessibility, applications, braille, voice, etc.
- **Android**: system apps, user, accessibility, widgets, etc. management
- **Console**: HDMI support, controllers, interface analysis.
- **Haptic**: tactile feedback, custom controllers.
- **Spatial Audio**: 3D sound, calibration, audio headsets.
- **Braille**: displays, translation, configuration.
- **AI/Models**: image recognition, OCR, interface description.

## Centralized Configuration
A configuration file allows managing all supports (voice, braille, haptic, AI, etc.) and adapting the user experience.

## Documentation
See the `docs/` folder for installation guides, technical documentation, video tutorials, etc.

## Contribution
Any help is welcome to make digital technology accessible and dignified for everyone!

## Vision
Make any digital content accessible (PC, Linux, Android, consoles, video games...) to everyone, through AI, multimodality (voice, braille, haptic, spatial sound...) and portable, non-invasive, open source solutions.

## Goals
- Universal accessibility, even for non-accessible video games
- Portable solution (USB key, Raspberry Pi, Android...)
- AI for image analysis, OCR, interface description
- Customizable restitution: voice, braille, haptic, spatial sound
- Modularity: each component can be used separately
- Community openness: everyone can contribute, adapt, enrich

## Use Cases
- Read and navigate in non-accessible video games
- Make a gaming console accessible via HDMI capture card
- Use AI to describe a graphical interface or menu
- Restitute information through voice, braille, haptic feedback or spatial sound

## How to contribute?
- Fork the project, propose your modules, fix documentation, share your ideas!
- Any contribution (code, documentation, tests, hardware, ideas) is welcome.

## To go further
- See specific folders for each modality
- Installation and usage guides in `docs/`
- Code examples in each subfolder

---

**This project is open, evolving, and awaits your ideas to make digital technology truly accessible to everyone!** 