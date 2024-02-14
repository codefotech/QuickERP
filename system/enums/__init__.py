class CustomEnum:
    def __init__(self, **kwargs):
        self.enum_data = kwargs

    def __getattr__(self, item):
        if item in self.enum_data:
            return self.enum_data[item]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")


    def __setattr__(self, key, value):
        if key != 'enum_data':
            raise AttributeError("Cannot set attributes directly in CustomEnum")
        super().__setattr__(key, value)

    def keys(self):
        return self.enum_data.keys()

    def values(self):
        return self.enum_data.values()

# Example usage:
# custom_enum = CustomEnum(key1='value1', key2='value2')

# print(custom_enum.key1)  # Accessing value using key
# print(custom_enum.keys()) # Getting keys
# print(custom_enum.values()) # Getting values
