import GROUPS as GROUPS
import NUMBER as NUMBER
import STR as STR
import SUBJECT as SUBJECT
import sly
import codecs


class MyLexer(sly.Lexer):
    # Set of token names.   This is always required
    tokens = {GROUPS, STR, NUMBER, SUBJECT, STUDENTS, L_, R_, COMMA}
    literals = {'\n', '\"', ' ', '.'}
    # String containing ignored characters between tokens
    ignore = ' \t\n'

    # Regular expression rules for tokens
    STR = r'([а-яА-я-\."][а-яА-я-\."0-9]*)([ ][а-яА-я-\."][а-яА-я-\."0-9]*){0,1}'
    STUDENTS = 'students'
    GROUPS = 'groups'
    SUBJECT = 'subject'
    NUMBER = r'\d+'
    L_ = r'\('
    R_ = r'\)'
    COMMA = r'\,'

    def error(self, t):
        self.index += 1


if __name__ == '__main__':
    lexer = MyLexer()
    fileObj = codecs.open("example.txt", "r", "utf_8_sig")
    data = fileObj.read()  # или читайте по строке
    fileObj.close()

    for tok in lexer.tokenize(data):
        print('type=%r, value=%r' % (tok.type, tok.value))
