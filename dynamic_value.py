class DynamicValueMeta(type):
    def __instancecheck__(self, instance):
        return self.__subclasscheck__(type(instance))

    def __subclasscheck__(self, subclass):
        return (hasattr(subclass, '__init__') and
                callable(subclass.__init__) and
                hasattr(subclass, 'is_valid') and
                callable(subclass.is_valid) and
                hasattr(subclass, 'get_random_value') and
                callable(subclass.get_random_value))


class DynamicValue(metaclass=DynamicValueMeta):
    pass
