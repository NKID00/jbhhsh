from cmd import Cmd

from jieba import initialize

from jbhhsh_core import Jbhhsh, join_words


class JbhhshCli(Cmd):
    intro = '直接进行一个句子的输入\nexit可以进行一个程序的退出'
    prompt = '>>> '

    def preloop(self):
        self.jbhhsh = Jbhhsh()

    def default(self, line: str) -> bool:
        if line == 'exit':
            return True

        result_words, replaced_words = self.jbhhsh.abbreviate_line(line)

        print(' ->', join_words(result_words))
        print()

        for key, trans, abbr in replaced_words:
            if key == trans:
                print(f' ** {trans} -> {abbr}')
            else:
                print(f' ** {key}: {trans} -> {abbr}')

        return False


def main():
    print('「就不好好说话！」缩写工具')
    print('进行一个版权的所有 (c) NKID00 2021')
    print('进行一个 MIT 执照的底下（under MIT License')
    print('进行一个结巴分词的初始化...')
    initialize()
    JbhhshCli().cmdloop()


if __name__ == '__main__':
    main()
