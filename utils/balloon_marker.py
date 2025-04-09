
class BalloonMarker:
    def __init__(self, x, y, number, color="#2196F3", size=1.0, shape="circle", dimension="", tolerance="", remarks=""):
        self.x = x
        self.y = y
        self.number = number
        self.color = color
        self.size = size
        self.shape = shape
        self.dimension = dimension  # New property
        self.tolerance = tolerance  # New property
        self.remarks = remarks      # New property
        self.selected = False

    def contains_point(self, x, y):
        # Check if point is within balloon (using circle hitbox for simplicity)
        radius = 14 * self.size
        dist_sq = (self.x - x) ** 2 + (self.y - y) ** 2
        return dist_sq <= radius ** 2

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def set_color(self, color):
        self.color = color

    def set_size(self, size):
        self.size = size

    def set_shape(self, shape):
        self.shape = shape

    def set_dimension(self, dimension):
        self.dimension = dimension

    def set_tolerance(self, tolerance):
        self.tolerance = tolerance

    def set_remarks(self, remarks):
        self.remarks = remarks
