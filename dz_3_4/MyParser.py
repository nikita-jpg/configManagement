import codecs
import json

from sly import Parser
from MyLexer import MyLexer

myBNF = '''
    <program> ::= '(' <s-list> ')' 
                |    
    <s-list> ::= <s-exp> <s-list>
                |                    
    <s-exp> ::= '(' <s-list> ')' 
                | '('<students>')' '('<groups>')' '('<subject>')'
    <students> ::= <students_> <students>
                | <student> <students>
                |
    <student> ::= '('<name_str> <age_number> <group_str>')' 
    <groups> ::= <groups_> '('<from_number> ',' <to_number>')' '('<group_str>')' 
    <subject> ::= <subject_> "\""<str>"\""   
    <name_str> ::= "\""<str>"\""
    <group_str> ::= <str>
    <age_number> ::= <int> 
    <from_number> ::= <int> 
    <to_number> ::= <int> 
    <int> ::= integer
    <str> ::= string
    <students_> ::= 'students' 
    <groups_> ::= 'groups'
    <subject_> ::= 'subject'
'''


class Student(object):
    def __init__(self, name, age, group):
        self.name = name
        self.age = int(age)
        self.group = group

    def __str__(self):
        return "\t{\n\t \"age\": " \
               + "\"" + str(self.age) + "\"" + ",\n\t \"group\": " \
               + "\"" + str(self.group) + "\"" + ",\n\t \"name\": " \
               + "\"" + str(self.name) + "\"" + "\n\t}"


class Subject(object):
    def __init__(self, subject):
        self.subject = subject

    def __str__(self):
        return "{\n\"subject\": " \
               + str(self.subject) + "\n}"


class MyParser(Parser):
    # Get the token list from the lexer (required)
    tokens = MyLexer.tokens

    # Grammar rules and actions
    @_(' s_list ')
    def data(self, p):
        return p.s_list

    @_(' s_exp s_list ')
    def s_list(self, p):
        return p.s_exp

    @_('')
    def s_list(self, p):
        pass

    @_(' L_ groups R_ L_ students R_ L_ subject R_ ')
    def s_exp(self, p):
        return "{\n\"groups\":" + str(p.groups) + "\n" + "\"students\": {\n" + p.students + "}\n" + str(p.subject) + '\n}'

    @_(' L_ s_list R_ ')
    def s_exp(self, p):
        return p.s_list

    @_('STUDENTS students')
    def students(self, p):
        return p.students

    @_('')
    def students(self, p):
        return ""

    @_(' student students')
    def students(self, p):
        return str(str(p.student) + "\n" + str(p.students))

    @_(' L_ name_str age_number group_str R_ ')
    def student(self, p):
        student = Student(p.name_str, p.age_number, p.group_str)
        return student

    @_('GROUPS L_ from_number COMMA to_number R_ L_ group_str R_')
    def groups(self, p):
        group_list = [p.group_str[:5] + str(c) + p.group_str[7:] for c in range(p.from_number, p.to_number + 1)]
        return group_list

    @_('STR')
    def name_str(self, p):
        name = str(p.STR)
        return name[1:len(name)-1]

    @_('NUMBER')
    def age_number(self, p):
        return int(p.NUMBER)

    @_('STR')
    def group_str(self, p):
        group_name = str(p.STR)
        return group_name[1:len(group_name)-1]

    @_('NUMBER')
    def to_number(self, p):
        return int(p.NUMBER)

    @_('NUMBER')
    def from_number(self, p):
        return int(p.NUMBER)

    @_('SUBJECT STR')
    def subject(self, p):
        subject_name = str(p.STR)
        subject = Subject(subject_name[1:len(subject_name) - 1])
        return subject


if __name__ == '__main__':

    lexer = MyLexer()
    parser = MyParser()
    fileObj = codecs.open("example.txt", "r", "utf_8_sig")
    data = fileObj.read()  # или читайте по строке
    result = parser.parse(lexer.tokenize(data))
    print(result)
    fileObj.close()
