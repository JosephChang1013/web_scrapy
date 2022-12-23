import random
import re
import string
from typing import Dict, Any, Optional, List
from uuid import uuid4, uuid1


def dict_keys_to_camel_case(dictionary: Dict[str, Any]):
    result: Dict[str, Any] = dict()
    for key, value in dictionary.items():
        if isinstance(value, list):
            value = [dict_keys_to_camel_case(v) if isinstance(v, dict) else v for v in value]
        if isinstance(value, dict):
            value = dict_keys_to_camel_case(value)
        if isinstance(key, str):
            key = to_camel_case(key)
        result[key] = value
    return result


def to_camel_case(value: str):
    return ''.join(word if index == 0 else word.title() for index, word in enumerate(value.split('_')))


def to_snake_case(value: str):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()


def generate_key(size: int, include_symbols=False, include_digits=True, include_lower=True, include_upper=True):
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation
    # string.ascii_letters
    possibles = ''
    if include_lower:
        possibles += lower
    if include_upper:
        possibles += upper
    if include_digits:
        possibles += num
    if include_symbols:
        possibles += symbols

    possibles = [c for c in possibles if c not in ['\'', '\\', '"']]
    temp = random.sample(possibles * 10, size)
    password = "".join(temp)
    return password


def parse_list_of_string(list_str: str) -> Optional[List[str]]:
    if list_str.startswith('[') and list_str.endswith(']'):
        content = list_str[1:-1]
        if content:
            elements = [elem.strip() for elem in content.split(',')]
            if all(elem.startswith('"') and elem.endswith('"') for elem in elements):
                return [elem[1:-1] for elem in elements]
            return None
        return list()
    return None


def uuid1_string() -> str:
    return str(uuid1().hex)


def uuid4_string() -> str:
    return str(uuid4().hex)


def has_zh(word: str):
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    match = zh_pattern.search(word)
    return bool(match)


def replaces(word: str, finds: List[str], replace: str) -> str:
    for find in finds:
        word = word.replace(find, replace)
    return word


if __name__ == '__main__':
    # print(to_camel_case("test_something"))
    # print(dict_keys_to_camel_case({"test_a": 100, "test_b": {"test_di": 1}, "test_c": [{"test_gd": 2}, {"test_aa": 3}], "test_das": ["asd_d", "dsa_a"]}))
    # print(replaces('<> {} {} 123', ['{}', '<>'], 'a'))
    print(generate_key(512, include_symbols=False))
