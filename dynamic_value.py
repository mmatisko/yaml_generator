class DynamicValueMeta(type):
    def __instancecheck__(self, instance):
        return self.__subclasscheck__(type(instance))

    def __subclasscheck__(self, subclass):
        methods: list = ['__init__', 'get_random_value']
        attribs: list = ['is_valid']

        for fnc in methods:
            if not hasattr(subclass, fnc) or not callable(getattr(subclass, fnc)):
                return False
        for attr in attribs:
            if not hasattr(subclass, attr) or callable(getattr(subclass, attr)):
                return False
        return True


class DynamicValue(metaclass=DynamicValueMeta):
    pass
