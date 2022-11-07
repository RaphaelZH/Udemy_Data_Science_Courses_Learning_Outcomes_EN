import re
from tabulate import tabulate
from termcolor import cprint

from .RandomColors import color_list_generator


class Form_Generator:
    def __init__(self):
        self.adjusted_width = 59

    def heading_printer(self, heading):
        self.heading = heading
        global font_colors_list
        try:
            font_colors_list
        except NameError:
            font_colors_list = color_list_generator()
        if font_colors_list == []:
            font_colors_list = color_list_generator()
        self.previous_color = font_colors_list.pop(0)
        cprint(self.heading, self.previous_color, attrs=["underline"], end="\n\n")

    def tabulator_replacement(self, string, expandtabs):
        if len(re.findall(r"\t", string)) > 0:
            string = re.sub(r"\t", " " * expandtabs, string)
        return string

    def string_trimmer(self, string, expandtabs, width):
        printable_lines = []
        string = self.tabulator_replacement(string, expandtabs)
        printable_line = string
        if len(string) > width:
            printable_line = string
            while len(printable_line) > width:
                while printable_line.rfind(" ") > width:
                    printable_line = printable_line[: printable_line.rfind(" ")]
                printable_line = printable_line[: printable_line.rfind(" ")]
                printable_lines.append(printable_line)
                string = string[len(printable_line) + 1 :]
                printable_line = string
        printable_lines.append(printable_line)
        return printable_lines

    def statement_generator(self, statements):
        table = [["Statement"]]
        for statement in statements:
            printable_lines = [
                "\n\t".expandtabs(8).join(
                    self.string_trimmer(line, 4, self.adjusted_width)
                )
                for line in statement.strip().split("\n")
            ]
            table.append(["\n".join(printable_lines)])
        table_list = tabulate(
            table, headers="firstrow", tablefmt="grid", colalign=("left",)
        ).split("\n")
        for line in table_list:
            cprint("\t".expandtabs(4) + line, self.previous_color, attrs=["bold"])

    def definition_generator(self, definitions):
        table = [["Definition"]]
        for definition in definitions:
            printable_lines = [
                "\n\t".expandtabs(8).join(
                    self.string_trimmer(line, 4, self.adjusted_width)
                )
                for line in definition.strip().split("\n")
            ]
            table.append(["\n".join(printable_lines)])
        table_list = tabulate(
            table, headers="firstrow", tablefmt="grid", colalign=("left",)
        ).split("\n")
        for line in table_list:
            cprint("\t".expandtabs(4) + line, self.previous_color, attrs=["bold"])

    def expression_generator(self, expressions, results):
        table = [["Expression", "Result"]]
        max_length = len(max(expressions, key=len))
        length_expression = max(len("Expression"), max_length)
        remainder = self.adjusted_width - length_expression - 3
        for expression, result in zip(expressions, results):
            printable_lines = [
                "\n\t".expandtabs(8).join(self.string_trimmer(line, 8, remainder))
                for line in result.strip().split("\n")
            ]
            table.append([expression, "\n".join(printable_lines)])
        table_list = tabulate(
            table, headers="firstrow", tablefmt="pretty", colalign=("left", "left")
        ).split("\n")
        for line in table_list:
            cprint("\t".expandtabs(4) + line, self.previous_color, attrs=["bold"])

    def variable_generator(self, variables, values):
        table = [["Variable", "Value"]]
        max_length = len(max(variables, key=len))
        length_variable = max(len("Variable"), max_length)
        remainder = self.adjusted_width - length_variable - 3
        for variable, value in zip(variables, values):
            if len(value) > remainder:
                printable_value = ""
                if re.search(r"\n", str(value)):
                    start = 0
                    string_list = []
                    for match in re.finditer(r"\n", str(value)):
                        nested_string = str(value)[start : match.span()[0]]
                        string_list.append(nested_string)
                        start = match.span()[1]
                    string_list.append(str(value)[start:])
                    for nested_string in string_list:
                        if (
                            len(nested_string)
                            + len(re.findall(r"\t", nested_string)) * 8
                            > remainder
                        ):
                            printable_string = ""
                            printable_line = nested_string
                            while (
                                len(printable_line)
                                + len(re.findall(r"\t", printable_line)) * 8
                                > remainder
                            ):
                                while (
                                    printable_line.rfind(" ")
                                    + len(re.findall(r"\t", printable_line)) * 8
                                    > remainder
                                ):
                                    printable_line = printable_line[
                                        : printable_line.rfind(" ")
                                    ]
                                printable_line = printable_line[
                                    : printable_line.rfind(" ")
                                ]
                                printable_string += printable_line.expandtabs(8) + "\n"
                                nested_string = nested_string[len(printable_line) + 1 :]
                                printable_line = nested_string.expandtabs(8)
                            printable_string += printable_line.expandtabs(8)
                            printable_value += printable_string.expandtabs(8) + "\n"
                        else:
                            printable_value += nested_string + "\n"
                    table.append([variable, printable_value.strip("\n")])
                else:
                    printable_line = value
                    while len(value) > remainder:
                        while printable_line.rfind(" ") > remainder:
                            printable_line = printable_line[: printable_line.rfind(" ")]
                        printable_line = printable_line[: printable_line.rfind(" ")]
                        printable_value += printable_line + "\n"
                        value = value[len(printable_line) + 1 :]
                        printable_line = value
                    printable_value += printable_line
                    table.append([variable, printable_value])
            else:
                table.append([variable, value])
        table_list = tabulate(
            table, headers="firstrow", tablefmt="pretty", colalign=("left", "left")
        ).split("\n")
        for line in table_list:
            cprint("\t".expandtabs(4) + line, self.previous_color, attrs=["bold"])
