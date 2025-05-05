# AstralTrail3D

AstralTrail3D is a homebrewed 3D rendering program developed as a self-taught programming challenge. This project showcases the fundamentals of 3D graphics, including rendering, transformations, and lighting, all built from scratch.

## Features

- **Custom 3D Rendering Engine**: Built with OpenGL/Pyglet
- **Basic Transformations**: Translation, rotation, and scaling of 3D objects.
- **Lighting**: Simple lighting models for realistic shading.
- **Camera Controls**: Navigate and explore the 3D scene.
- **Object Loading**: Support for basic 3D object formats.

## Motivation

This project was created as a personal challenge to learn and implement the core concepts of 3D graphics programming. It serves as a testament to the power of self-learning and the joy of building something from the ground up.

## Technologies Used

- **Programming Language**: Python 3.13.2
- **Math Libraries**: numpy
- **Rendering Framework**: using pyglet wrappers for OpenGL contexts

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/cmbains12/AstralTrail3D.git
    cd AstralTrail3D
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the program:
    ```bash
    python __main__.py
    ```

## Usage

- Use the keyboard and mouse to navigate the 3D scene.
- 'wasd' controls, 'lshift' and 'space' for descend and ascend.
- mouse movement controlls look direction in an uninverted FPS control scheme.
- Must modify gamestate.py file to change what is rendered (object generation UI in progress...)
- No execution argument support at the moment, and always runs in test mode.

## Challenges Faced

- Implementing 3D transformations and projections from scratch.
- Understanding and applying lighting models.
- Optimizing performance for real-time rendering.
- OpenGL and GLSL fluency

## Future Improvements

- Add support for advanced lighting techniques (e.g., shadows, reflections).
- Implement texture mapping.
- Expand support for additional 3D file formats.

## Acknowledgments


## License

This project is licensed under the [MIT License](LICENSE).

---
Feel free to contribute, report issues, or share your feedback!