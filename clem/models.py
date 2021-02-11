import random
import re
from typing import Dict, List, Optional, Union

# Type aliases
ClemContent = List[Union['Choice', 'Decision', 'Keyword', str]]


class Choice:
    odds_pattern = re.compile(r'(^(?:\d+:)?)(.*)')

    def __init__(self, content: ClemContent, odds: int = 1):
        self.content: ClemContent = content
        self.odds: int = odds

    def __repr__(self) -> str:
        return f'<Choice (Odds: {self.odds})>'

    @staticmethod
    def parse(content: List[str]) -> 'Choice':
        """ Constructs a `Choice` from Clem syntax.
        """
        # Get odds declaration if it exists, default to 1 otherwise
        if type(content[0]) == str:
            odds, text = Choice.odds_pattern.match(content[0]).groups()
            if odds:
                odds = int(re.match(r'(\d+):', odds).group(1))
            else:
                odds = 1
            content[0] = text.strip()
        else:
            odds = 1

        return Choice(content=content, odds=odds)


class Clem:
    """ Handles top-level file loading and user interaction.
    """
    def __init__(self):
        self.lines: Dict[str, Line] = dict()

    def add(self, text: str, section: Optional[str] = None):
        """ Parses raw Clem line and adds it to list.
        """
        # Ignore commented lines
        if text.strip().startswith('#'):
            return
        line = Line(text)

        # Insert line into appropriate list (create it if nonexistent)
        identifier = f'{section or line.identifer}.{line.identifier}'
        self.lines[identifier] = self.lines.get(identifier, list())
        self.lines[identifier].append(line)

    def find(self, identifier: str) -> Optional['Line']:
        """ Returns random line with matching identifier.
        """
        lines = self.lines.get(identifier)
        if lines:
            return random.choice(lines)

    def load_file(self, filename: str):
        """ Load and parse whole .clem file into line list.
        """
        # Load lines from file and strip whitespace/blank lines
        with open(filename, 'r', encoding='utf-8') as f:
            file_contents = (line.strip() for line in f.readlines()
                             if line.strip())

        # Parse lines and insert them into line list
        section = ''
        for line in file_contents:
            if Line.section_pattern.match(line):
                section = Line.section_pattern.match(line).group(1)
            elif line.strip() == ')':
                section = ''
            elif Line.clem_line_pattern.match(line):
                self.add(line, section)

    def render(self, identifier: str, **keywords: Dict[str, str]) \
            -> Optional[str]:
        """ Renders a random line by `identifier`.
        """
        line = self.find(identifier)
        if line:
            return line.render(**keywords)


class Decision:
    """ A collection of mutually exclusive Choices>
    """
    def __init__(self, choices: List[Choice]):
        self.choices: List[Choice] = choices
        if len(self.choices) < 2:
            self.choices.append(Choice(content='', odds=1))

    def __repr__(self) -> str:
        return f'<Decision (n={len(self.choices)})>'

    def decide(self) -> ClemContent:
        """ Rasterizes decision into content of one of choices.
        """
        options = list()

        # Add choices into options, appearing relative to their odds
        for choice in self.choices:
            options += [choice] * choice.odds

        return random.choice(options).content


class Keyword:
    """ A placeholder for a variable.
    """
    def __init__(self, name: str):
        self.name: str = name

    def __repr__(self) -> str:
        return f'<Keyword {self.name!r}>'

    @staticmethod
    def parse(text: str) -> ClemContent:
        """ Parses text for Keywords and returns resulting content.
        """
        reset_point = 0
        content = list()
        for idx, c in enumerate(text):
            if c == '{':
                content.append(text[reset_point:idx])
                reset_point = idx
            elif c == '}':
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


class Line:
    """ An entire Clem line.
    """
    section_pattern: re.Pattern = re.compile(r'^\s*(\w+)\s*\(')
    clem_line_pattern: re.Pattern = re.compile(r'^\s*\w+\s*\|.+')
    indentifier_pattern: re.Pattern = re.compile(r'^(\S+)\s?\|(.*)')

    def __init__(self, text: str):
        identifier, content = Line.indentifier_pattern.match(text).groups()
        self.identifier: str = identifier
        self.content: ClemContent = Line.parse(content.strip())

    def __repr__(self) -> str:
        return f'<Line {self.identifier!r}>'

    def render(self, **keywords: Dict[str, str]) -> str:
        """ Renders line as a string. This will flatten all decisions and
            rasterize all Keywords using `keywords`.
        """
        return Line.clean_whitespace(Line.flatten(self.content, **keywords))

    @staticmethod
    def clean_whitespace(text: str) -> str:
        """ Removes surplus whitespace introduced by tokenization and
            rasterization processes.
        """
        # Clean excessive spaces
        text = re.sub(r'\s+([\s.,!?:;)])', r'\1', text.strip())
        # Remove spaces following opening characters
        text = re.sub(r'([(\'"])\s+', r'\1', text)

        return text

    @staticmethod
    def flatten(content, **keywords: Dict[str, str]) \
            -> Union[ClemContent, List[ClemContent]]:
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
                return ' '.join((s.strip() for s in new_content))
            return Line.flatten(new_content, **keywords)
        else:
            return content

    @staticmethod
    def parse(text: str) -> ClemContent:
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
            if c == '<':
                if level == 0:
                    if idx > 0:
                        content.append(Keyword.parse(text[descension:idx]))
                    ascension = idx
                level += 1
            # Descend a bracket level
            elif c == '>':
                level -= 1
                if level == 0:
                    descension = idx + 1
                    # Recursively parse decision content
                    decision_content = Line.parse(
                        text[ascension + 1:descension - 1]
                    )
                    # If only one choice, make into Decision.
                    # (Will otherwise be ignored)
                    if type(decision_content) is not Decision:
                        decision_content = Decision(
                            [Choice.parse([decision_content])]
                        )
                    content.append(decision_content)
            # New top-level choice
            elif c == '/' and level == 0:
                # Dump remaining text into content buffer
                content.append(Keyword.parse(text[descension:idx]))
                # Append content buffer into choices list and clear buffer
                choices.append(content)
                content = list()
                # Store reset point
                descension = idx + 1

        if level > 0:
            raise SyntaxError(f'Expected \'>\', got EOL. (Level: {level})')
        elif level < 0:
            raise SyntaxError(f'Unexpected \'>\'. (Level: {level})')
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
