import numpy as np

class Camera:
    def __init__(self, **kwargs):
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.orientation_x = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        self.orientation_y = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.orientation_z = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        self.orientation = np.array([
            self.orientation_x,
            self.orientation_y,
            self.orientation_z
        ], dtype=np.float32)
        self.fov = 60.0
        self.aspect = 1.0
        self.near_plane = 0.1
        self.far_plane = 100.0

        self.move_speed = 2.0
        self.turn_speed = 90.0

        if 'fov' in kwargs:
            self.fov = kwargs['fov']
        if 'aspect' in kwargs:
            self.aspect = kwargs['aspect']
        if 'near_plane' in kwargs:
            self.near_plane = kwargs['near_plane']
        if 'far_plane' in kwargs:
            self.far_plane = kwargs['far_plane']

        f = 1.0 / np.tan(np.radians(self.fov) / 2.0)
        asp = self.aspect
        z_factor = -(self.far_plane + self.near_plane) / (self.far_plane - self.near_plane)
        z_offset = (-2.0 * self.far_plane * self.near_plane) / (self.far_plane - self.near_plane)

        self.projection_matrix = np.array([
            [f / asp, 0.0, 0.0, 0.0],
            [0.0, f, 0.0, 0.0],
            [0.0, 0.0, z_factor, z_offset],
            [0.0, 0.0, -1.0, 0.0]
        ], dtype=np.float32).T.flatten()

        if 'position' in kwargs:
            self.position = kwargs['position']

        if 'orientation' in kwargs:
            self.orientation_x = kwargs['orientation'][0]
            self.orientation_y = kwargs['orientation'][1]
            self.orientation_z = kwargs['orientation'][2]
            self.orientation = kwargs['orientation']

        params = [kwargs[param] for param in ['orientation_x', 'orientation_y', 'orientation_z'] if param in kwargs]
        if len(params) == 1:
            if 'orientation_z' in kwargs:
                self.orientation_z = kwargs['orientation_z']
                self.orientation_x = np.cross(np.array([0.0, 1.0, 0.0], dtype=np.float32), self.orientation_z)
                self.orientation_y = np.cross(self.orientation_z, self.orientation_x)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
            elif 'orientation_x' in kwargs:
                self.orientation_x = kwargs['orientation_x']
                self.orientation_z = np.cross(self.orientation_x, np.array([0.0, 1.0, 0.0], dtype=np.float32))
                self.orientation_y = np.cross(self.orientation_z, self.orientation_x)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
            elif 'orientation_y' in kwargs:
                self.orientation_y = kwargs['orientation_y']
                self.orientation_z = np.cross(np.array([1.0, 0.0, 0.0], dtype=np.float32), self.orientation_y)
                self.orientation_x = np.cross(self.orientation_y, self.orientation_z)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
        elif len(params) == 2:
            if not 'orientation_y' in kwargs:
                self.orientation_y = np.cross(self.orientation_z, self.orientation_x)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)

            elif not 'orientation_z' in kwargs:
                self.orientation_z = np.cross(self.orientation_x, self.orientation_y)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)

            elif not 'orientation_x' in kwargs:
                self.orientation_x = np.cross(self.orientation_y, self.orientation_z)
                self.orientation = np.array([
                    self.orientation_x,
                    self.orientation_y,
                    self.orientation_z
                ], dtype=np.float32)
        elif len(params) == 3:
            self.orientation_x = kwargs['orientation_x']
            self.orientation_y = kwargs['orientation_y']
            self.orientation_z = kwargs['orientation_z']
            self.orientation = np.array([
                self.orientation_x,
                self.orientation_y,
                self.orientation_z
            ], dtype=np.float32)

    @property
    def view_matrix(self):
        vm1 = np.array([
            [1.0, 0.0, 0.0, -self.position[0]],
            [0.0, 1.0, 0.0, -self.position[1]],
            [0.0, 0.0, 1.0, -self.position[2]],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        vm2 = np.array([
            [self.orientation_x[0], self.orientation_x[1], self.orientation_x[2], 0.0],
            [self.orientation_y[0], self.orientation_y[1], self.orientation_y[2], 0.0],
            [self.orientation_z[0], self.orientation_z[1], self.orientation_z[2], 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        return (vm2 @ vm1).T.flatten()

    def move_forward(self, delta_time, mode='flat'):
        direction = self.orientation_z.copy()
        if mode == 'flat':
            direction[1] = 0.0
            direction /= np.linalg.norm(direction)
        self.position -= direction * self.move_speed * delta_time

    def move_backward(self, delta_time, mode='flat'):
        direction = self.orientation_z.copy()
        if mode == 'flat':
            direction[1] = 0.0
            direction /= np.linalg.norm(direction)
        self.position += direction * self.move_speed * delta_time

    def move_left(self, delta_time, mode='flat'):
        direction = self.orientation_x.copy()
        if mode == 'flat':
            direction[1] = 0.0
            direction /= np.linalg.norm(direction)
        self.position -= direction * self.move_speed * delta_time

    def move_right(self, delta_time, mode='flat'):
        direction = self.orientation_x.copy()
        if mode == 'flat':
            direction[1] = 0.0
            direction /= np.linalg.norm(direction)
        self.position += direction * self.move_speed * delta_time

    def move_up(self, delta_time):
        direction = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.position += direction * self.move_speed * delta_time

    def move_down(self, delta_time):
        direction = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.position -= direction * self.move_speed * delta_time
    '''
    def turn_left(self, delta_time):
        angle = np.radians(self.turn_speed * delta_time)
        rotation_matrix = np.array([
            [np.cos(angle), 0.0, np.sin(angle)],
            [0.0, 1.0, 0.0],
            [-np.sin(angle), 0.0, np.cos(angle)]
        ], dtype=np.float32)
        self.orientation_z = rotation_matrix @ self.orientation_z
        self.orientation_x = rotation_matrix @ self.orientation_x
        self.orientation_y = rotation_matrix @ self.orientation_y

    def turn_right(self, delta_time):
        angle = np.radians(-self.turn_speed * delta_time)
        rotation_matrix = np.array([
            [np.cos(angle), 0.0, np.sin(angle)],
            [0.0, 1.0, 0.0],
            [-np.sin(angle), 0.0, np.cos(angle)]
        ], dtype=np.float32)
        self.orientation_z = rotation_matrix @ self.orientation_z
        self.orientation_x = rotation_matrix @ self.orientation_x
        self.orientation_y = rotation_matrix @ self.orientation_y

        self.orientation = rotation_matrix @ self.orientation
    '''
    def look_around(self, dx, dy):
        angle_y = np.radians(-dx * self.turn_speed / 1000.0)
        angle_x = np.radians(dy * self.turn_speed / 1000.0)
        axisx = self.orientation[0]
        x = axisx[0]
        y = axisx[1]
        z = axisx[2]
        c = np.cos(angle_x)
        s = np.sin(angle_x)

        rotate_x = np.array([
            x * x * (1 - c) + c, x * y * (1 - c) - z * s, x * z * (1 - c) + y * s,
            y * x * (1 - c) + z * s, y * y * (1 - c) + c, y * z * (1 - c) - x * s,
            z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, z * z * (1 - c) + c
        ], dtype=np.float32).reshape(3, 3)

        self.orientation = (rotate_x @ self.orientation.T).T
        self.orientation_x = self.orientation[0]
        self.orientation_y = self.orientation[1]
        self.orientation_z = self.orientation[2]

        axisy = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        x = axisy[0]
        y = axisy[1]
        z = axisy[2]
        c = np.cos(angle_y)
        s = np.sin(angle_y)
        rotate_y = np.array([
            x * x * (1 - c) + c, x * y * (1 - c) - z * s, x * z * (1 - c) + y * s,
            y * x * (1 - c) + z * s, y * y * (1 - c) + c, y * z * (1 - c) - x * s,
            z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, z * z * (1 - c) + c
        ], dtype=np.float32).reshape(3, 3)
        
        self.orientation = (rotate_y @ self.orientation.T).T





        