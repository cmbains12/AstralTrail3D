# AstralTrail3D

AstralTrail3D is a homebrewed 3D rendering program developed as a self-taught programming challenge. This project showcases the fundamentals of 3D graphics, including rendering, transformations, and lighting, all built from scratch.

## Features

- **Custom 3D Rendering Engine**: Built without external graphics libraries.
- **Basic Transformations**: Translation, rotation, and scaling of 3D objects.
- **Lighting**: Simple lighting models for realistic shading.
- **Camera Controls**: Navigate and explore the 3D scene.
- **Object Loading**: Support for basic 3D object formats.

## Motivation

This project was created as a personal challenge to learn and implement the core concepts of 3D graphics programming. It serves as a testament to the power of self-learning and the joy of building something from the ground up.

## Technologies Used

- **Programming Language**: Python 3.13.2
- **Math Libraries**: built-in python math library
- **Rendering Framework**: using pygame 2.6.1 surface object, line, circle, polygon methods.

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
    python main.py
    ```

## Usage

- Use the keyboard (mouse support in progress...) to navigate the 3D scene.
- 'wasd' controls, 'q' and 'e' to pan left and right, 'lshift' and 'space' for descend and ascend, and 'r' and 'f' for pan down and up (inverted atm).
- Must modify gamestate.py file to change what is rendered (object generation UI in progress...)
- No execution argument support at the moment, and always runs in test mode.

## Challenges Faced

- Implementing 3D transformations and projections from scratch.
- Understanding and applying lighting models.
- Optimizing performance for real-time rendering.

## Future Improvements

- Add support for advanced lighting techniques (e.g., shadows, reflections).
- Implement texture mapping.
- Optimize rendering pipeline for better performance.
- Expand support for additional 3D file formats.

## Acknowledgments

- I acknowledge that I should have paid closer attention to Linear Algebra I and Linear Algebra II classes.

## License

This project is licensed under the [MIT License](LICENSE).

---
Feel free to contribute, report issues, or share your feedback!