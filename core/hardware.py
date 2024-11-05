class Hardware:
    def __init__(self, hardware_type, architecture):
        self.hardware_type = hardware_type
        self.architecture = architecture

    def __repr__(self):
        return f"Hardware(type={self.hardware_type}, architecture={self.architecture})"

    def to_dict(self):
        return {
            "hardware_type": self.hardware_type,
            "architecture": self.architecture
        }
