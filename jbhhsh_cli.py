from cmd import Cmd
from collections import deque
from random import choice

from jieba import initialize, cut

from jbhhsh_core import Jbhhsh


class JbhhshCli(Cmd):
    prompt = '>>> '

    def preloop(self):
        self.jbhhsh = Jbhhsh()

    def default(self, line: str) -> bool:
        if line == 'exit':
            return True

        # if line.startswith(('%', '(', '（', ')', '）')):
        #     line = line[1:]
        #     if line.startswith('%'):
        #         result = self.jbhhsh.search_wildcard(line)
        #     else:
        #         result = self.jbhhsh.search_parenthesis(line)
        #     if len(result) > 0:
        #         print('\n'.join(map(
        #             lambda item: f'{item[0]}: {", ".join(item[1])}',
        #             result.items()
        #         )))
        #     else:
        #         print('(none)')
        # else:
        #     result = self.jbhhsh.search(line)
        #     if len(result) > 0:
        #         print(', '.join(result))
        #     else:
        #         print('(none)')

        words = list(cut(line))
        result_words = deque()
        replaced_words = deque()
        i = 0
        while i < len(words):
            j = len(words)
            for j in range(len(words), i, -1):
                key = ''.join(words[i:j])
                result = self.jbhhsh.search(key)
                if len(result) > 0:
                    trans, abbr = choice(list(result.items()))
                    abbr = choice(abbr)
                    result_words.append(abbr)
                    replaced_words.append((key, trans, abbr))
                    i = j
                    break
            else:
                result_words.append(words[i])
                i += 1

        latest_word_is_ascii = False
        result = ''
        for word in result_words:
            if word.isascii():
                if latest_word_is_ascii:
                    result += ' '
                latest_word_is_ascii = True
            else:
                latest_word_is_ascii = False
            result += word
        print(' ->', result)
        print()

        for key, trans, abbr in replaced_words:
            if key == trans:
                print(f' ** {trans} -> {abbr}')
            else:
                print(f' ** {key}: {trans} -> {abbr}')

        return False


def main():
    print('jbhhsh (c) NKID00 2021')
    print('进行一个 MIT 执照的底下（under MIT License')
    print('进行一个结巴分词的初始化...')
    initialize()  # jieba
    print('进行一个主的循环...')
    print('exit可以进行一个程序的退出...')
    JbhhshCli().cmdloop()


if __name__ == '__main__':
    main()
