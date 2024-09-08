import copy
import json
from os import PathLike
from pathlib import Path


class BaseObject:
    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__} [{self.__dict__}]"

    @property
    def data(self):
        _ = dict()
        for k, v in self.__dict__.items():
            if isinstance(v, list):
                _[k] = list(map(lambda x: x.data, v))
            elif isinstance(v, (str, int, float, bool)):
                _[k] = v
            else:
                _[k] = v.data
        return _

    @property
    def objects(self):
        _ = dict()
        for k, v in self.__dict__.items():
            if k in ["_json"]:
                continue
            _[k] = v
        return _


class Scheme:
    def __init__(self):
        self._json: dict | None = None

    def load(self, path: PathLike | str | Path):
        with open(path, mode="r", encoding="UTF-8") as p:
            self._json = json.load(p)
        for k, v in self._json.items():
            if k[-1] == "s" and isinstance(v, list):
                cls_name = k[:len(k)-1]
            else:
                cls_name = k
            if isinstance(v, dict):
                self.__setattr__(k, self._wrapDict(cls_name, v))
            elif isinstance(v, list):
                self.__setattr__(k, self._wrapList(cls_name, v))
            else:
                self.__setattr__(k, v)

        return self

    def to_dict(self):
        _ = dict()
        for k, v in self.__dict__.items():
            if k in ["_json"]:
                continue
            if isinstance(v, list):
                _[k] = list(map(lambda x: x.data, v))
            elif isinstance(v, (str, int, float, bool, dict)):
                _[k] = v
            else:
                _[k] = v.data
        return _

    def to_json(self, path: PathLike | str | Path):
        with open(path, mode="w", encoding="utf-8") as wf:
            json.dump(self.to_dict(), wf, ensure_ascii=False, indent=4)

    def _wrapDict(self, cls_name: str, value: dict):
        cls = type(cls_name, (BaseObject,), {})
        o = cls()
        for k, v in value.items():
            if isinstance(v, dict):
                if k[-1] == "s" and isinstance(v, list):
                    k_name = k[:len(k) - 1]
                else:
                    k_name = k
                o.__setattr__(k, self._wrapDict(k_name, v))
            elif isinstance(v, list):
                if k[-1] == "s" and isinstance(v, list):
                    k_name = k[:len(k) - 1]
                else:
                    k_name = k
                o.__setattr__(k, self._wrapList(k_name, v))
            else:
                o.__setattr__(k, v)

        return o

    def _wrapList(self, cls_name: str, values: list):
        os = list()
        for oj in values:
            if isinstance(oj, dict):
                os.append(self._wrapDict(cls_name, oj))
            elif isinstance(oj, list):
                os.append(self._wrapList(cls_name, oj))
            else:
                os.append(oj)
        return os

    @property
    def keys(self):
        _ = copy.copy(list(self.__dict__.keys()))
        _.remove("_json")
        return _

    @property
    def objects(self):
        _ = dict()
        for k, v in self.__dict__.items():
            if k in ["_json"]:
                continue
            _[k] = v
        return _


class ObjectiveParser:
    def __init__(self):
        self._data: Scheme | None = None

    def parse(self, path: PathLike | str | Path):
        self._data = Scheme()
        self._data.load(path)

        return self._data

    @property
    def data(self):
        return self._data


if __name__ == '__main__':
    p = ObjectiveParser()
    x = p.parse("scheme.json")
    x.schema.comment = "Изменена в ObjectiveParser"
    x.to_json("result.json")
