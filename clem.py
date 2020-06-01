from __future__ import annotations
import random
import re
from typing import List, Union

# Type aliases
Content = List[Union['Choice', 'Keyword', str]]


class LevelMismatch(BaseException):
    pass


class Keyword(object):
    def __init__(self, name):
        self.name: str = name

    def __repr__(self):
        return f'{{\'{self.name}\'}}'

    @staticmethod
    def parse(text):
        reset_point = 0
        content = list()
        for idx, c in enumerate(text):
            if c == "{":
                content.append(text[reset_point:idx])
                reset_point = idx
            elif c == "}":
                keyword_name = text[reset_point + 1:idx]
                content.append(Keyword(keyword_name))
                reset_point = idx + 1
        content.append(text[reset_point:])

        # Return original content if no keywords found
        # (This prevents nested lists that contain only one element)
        if len(content) > 1:
            return content
        else:
            return content[0]


class Decision(object):
    def __init__(self, choices: List[Choice]):
        self.choices: List[Choice] = choices

    def __repr__(self):
        return f'<{" / ".join((str(choice) for choice in self.choices))}>'

    def decide(self):
        """ Flattens decision into contents by picking one option.
        """
        options = list()

        # Add choices into options, appearing relative to their odds
        for choice in self.choices:
            options += [choice] * choice.odds

        return random.choice(options).content


class Choice(object):

    odds_pattern = re.compile(r'(^(?:\d+:)?)(.*)')

    def __init__(self, content: Content, odds: int = 1):
        self.content: Content = content
        self.odds: int = odds

    def __repr__(self):
        return f"({self.odds}) {str(self.content)}"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def parse(content):
        # Get odds declaration if it exists, default to 1 otherwise
        if type(content[0]) == str:
            odds, text = Choice.odds_pattern.match(content[0]).groups()
            if odds:
                odds = int(re.match(r'(\d+):', odds).group(1))
            else:
                odds = 1
            content[0] = text
        else:
            odds = 1

        return Choice(content=content, odds=odds)


class Line(object):
    """ Represents a single Clem line.
    """

    indentifier_pattern: re.Pattern = re.compile(r'^(\S+)\s?\|(.*)')

    def __init__(self, text):
        identifier, content = Line.indentifier_pattern.match(text).groups()
        self.identifier: str = identifier
        self.content: Content = Line.parse(content.strip())

    def __repr__(self):
        return f'({self.identifier}) {self.content}'

    def render(self, **keywords):
        """ Flattens and renders line into regular string.
        """
        print(self.content)
        return Line.flatten(self.content, **keywords)

    @staticmethod
    def flatten(content, **keywords):
        """ Recursively flattens all contents into string.
        """
        new_content = list()
        for section in content:
            if type(section) is str:
                new_content.append(section)
            elif type(section) is Decision:
                new_el = section.decide()
                if type(new_el) is str:
                    new_content.append(new_el.strip())
                else:
                    if len(new_el) == 1:
                        new_content.append(new_el[0])
                    else:
                        new_content.append(new_el)
            elif type(section) is Keyword:
                new_content.append(keywords[section.name])
            elif type(section) is list:
                new_content += section
            else:
                input(section)
                new_content.append(section)

        if new_content:
            if all((type(s) is str for s in new_content)):
                return "".join(new_content)
            return Line.flatten(new_content, **keywords)
        else:
            return content

    @staticmethod
    def parse(text):
        # Level: Current bracket depth
        # Ascension: Index of first bracket
        # Descension: Index of last bracket / last reset point
        level, ascension, descension = 0, 0, 0
        # Content buffer stores everything until a choice marker
        content = list()
        # Choices stores the different content buffers
        choices = list()
        for idx, c in enumerate(text):
            # Ascend a bracket level
            if c == "<":
                if level == 0:
                    if idx > 0:
                        content.append(Keyword.parse(text[descension:idx]))
                    ascension = idx
                level += 1
            # Descend a bracket level
            elif c == ">":
                level -= 1
                if level == 0:
                    descension = idx + 1
                    # Append bracket level to content after parsing recursively
                    content.append(
                        Line.parse(text[ascension + 1:descension - 1])
                    )
            # New top-level choice
            elif c == "/" and level == 0:
                # Dump remaining text into content buffer
                content.append(Keyword.parse(text[descension:idx]))
                # Append content buffer into choices list and clear buffer
                choices.append(content)
                content = list()
                # Store reset point
                descension = idx + 1

        if level > 0:
            raise LevelMismatch(f'Expected \'>\', got EOL. (Level: {level})')
        elif level < 0:
            raise LevelMismatch(f'Unexpected \'>\'. (Level: {level})')
        # Append remaining text to content buffer if any
        if descension < len(text):
            content.append(Keyword.parse(text[descension:]))
        choices.append(content)

        if len(choices) > 1:
            # Make decision object out of choices
            return Decision([Choice.parse(choice) for choice in choices])
        else:
            # Return raw content
            if len(choices[0]) > 1:
                return choices[0]
            else:
                return choices[0][0]


class Clem(object):
    """ Master Clem object. Handles top-level file loading and user interaction.
    """
    def __init__(self):
        self.lines: List[Line] = list()

    def add(self, text):
        """ Parses raw Clem line and adds it to list.
        """


if __name__ == "__main__":
    with open("simple.clem", "r") as f:
        examples = f.readlines()

    result = Line(examples[0])
    print(examples[0])
    print(result.render(location="Brooklyn"))
