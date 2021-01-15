from collections import Iterable


class Serializable(object):
    def serialize(self):
        data = {}
        field_list = self.__slots__ if hasattr(self, '__slots__') else self.__dict__
        for field_name in field_list:
            format_method = getattr(self, 'get_{}'.format(
                field_name
            ), None)

            if format_method:
                data[field_name] = format_method()
            else:
                field: Serializable = getattr(self, field_name, None)
                if self._is_primary_type(field):
                    data[field_name] = field
                elif hasattr(field, 'serialize'):
                    data[field_name] = field.serialize()
                else:
                    data[field_name] = self._serialize_complex_field(field)
        return data

    def _serialize_complex_field(self, field):
        if self._is_primary_type(field):
            return field

        if hasattr(field, 'serialize'):
            return field.serialize()

        if self._is_dict(field):
            data = {}
            for key in field.keys():
                data[self._serialize_complex_field(key)] = self._serialize_complex_field(field[key])
            return data

        if self._is_list(field):
            data = []
            for item in field:
                data.append(self._serialize_complex_field(item))
            return data

    @staticmethod
    def _is_primary_type(field):
        return isinstance(field, str) or isinstance(field, int) or isinstance(field, float)

    @staticmethod
    def _is_iterable(field):
        return isinstance(field, Iterable)

    @staticmethod
    def _is_dict(field):
        return isinstance(field, dict)

    @staticmethod
    def _is_list(field):
        return isinstance(field, list) or isinstance(field, tuple)
