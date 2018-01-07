class Node:

    def __init__(self, name, keyPair):
        self.name = name
        self.keyPair = keyPair

    def get_images(self):
        raise NotImplementedError("Should have implemented this")

    def get_sizes(self):
        raise NotImplementedError("Should have implemented this")

    def get_image(self):
        raise NotImplementedError("Interface only")

    def get_size(self):
        raise NotImplementedError("Interface only")

    def set_image(self, imageID):
        raise NotImplementedError("This is the interface class")

    def set_size(self, size):
        raise NotImplementedError("This is the interface class")

    def instantiate_node(self):
        raise NotImplementedError("Should have implemented this")

    def attach_volume(self, volume):
        raise NotImplementedError("Should have implemented this")

    def dettach_volume(self, volume):
        raise NotImplementedError("Should have implemented this")