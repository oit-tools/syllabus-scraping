"""
データを解析
"""
import re


class Parser:
    def __init__(self):
        self.values = list()
        self.text = ""
        self.correction = 0  # 順番補正用

    def main(
        self,
        enter: str,
        department: str,
        url: str,
        dow: str,
        period: str,
        is_textbook: bool,
        is_reference_book: bool,
    ) -> dict:
        """
        csvを読み込み、jsonに変換
        """
        self.text = "\n".join(enter[1])

        try:
            lectures, themes, contents, preparations = list(), list(), list(), list()
            result = dict()

            keys = [
                "lecture_title",
                "lecture_title_en",
                "year",
                "credit",
                "term",
                "person",
                "numbering",
                "department",
                "url",
                "dow",
                "period",
                "aim",
                "cs",
                "spiral",
                "themes",
                "contents",
                "preparations",
                "target",
                "method",
                "basis",
                "textbook",
                "reference_book",
                "knowledge",
                "office_hour",
                "practice",
            ]

            # 講義名等を取得
            self.values.extend([enter[0][i] for i in range(len(enter[0]))])
            # 年次を削除
            self.values[2] = str(self.values[2]).replace("年次", "")
            # 担当者名のよみがな削除
            self.values[5] = re.sub(r"\(.+?\)", "", self.values[5]).replace("  ", ",")
            # 講義コードをurlから抽出し、追加
            numbering = re.search(r"\w{8}(?=&value)", url).group()
            self.values.append(numbering)
            # 学科追加
            self.values.append(department)
            # URL追加
            self.values.append(url)
            # 曜日
            self.values.append(dow)
            # 時限
            self.values.append(period)
            # 授業のねらい/概要
            self.values.append(enter[2][0])
            # CSコース
            self.cs_spiral("CSコース")
            # スパイラル型教育
            self.cs_spiral("スパイラル型教育")
            # 授業計画
            for i in range(1, (len(enter[3 + self.correction]))):
                lectures.append(str(enter[3 + self.correction][i]).split(","))
            for i in range(len(lectures)):
                if len(lectures[i][1]) > 0:
                    themes.append(lectures[i][1])
                if len(lectures[i][2]) > 0:
                    contents.append(lectures[i][2])
                if len(lectures[i][3]) > 0:
                    preparations.append(lectures[i][3])
            # テーマ
            self.lecture(themes)
            # 内容/方法
            self.lecture(contents)
            # 予習/復習
            self.lecture(preparations)
            # 目標、評価方法、評価基準
            self.values.extend([enter[4 + i + self.correction][0] for i in range(3)])
            # 教科書
            if is_textbook:
                self.textbook_reference_book(enter[7 + self.correction][1:])
            else:
                self.values.append("記載なし")
            # 参考書
            if is_reference_book:
                self.textbook_reference_book(enter[7 + self.correction][1:])
            else:
                self.values.append("記載なし")
            # 受講心得
            self.values.append(enter[7 + self.correction][0])
            # オフィスアワー
            self.values.append(enter[8 + self.correction][0])
            # 実践的教育
            if len(enter[9 + self.correction]) > 0:
                self.values.append(enter[9 + self.correction][0])
            else:
                self.values.append("記載なし")
            # 辞書に変換
            result.update({numbering: dict(zip(keys, self.values))})

        except Exception as e:
            with open("error.log", "w") as f:
                f.write(f"{e}\n{url}")

        finally:
            return result

    def cs_spiral(self, search_word):
        """
        CSコース、スパイラル型教育用の処理
        """
        text = self.text.replace("\\n", "")
        if search_word in text:
            word = re.search(rf"{search_word},(.*)", text).group(1)
            if len(word) > 0:
                self.values.append(word)
                self.correction += 1
            else:
                self.values.append("記載なし")
        else:
            self.values.append("記載なし")

    def textbook_reference_book(self, enter):
        """
        教科書、参考書用の処理
        """
        result = list()

        for i in range(len(enter)):
            result.append(enter[i].split(",")[1:])
        for i in range(len(result)):
            for j in range(len(result[i])):
                if len(result[i][j]) == 0:
                    result[i][j] = "記載なし"

        self.correction += 1
        self.values.append(result)

    def lecture(self, name):
        """
        授業計画用の処理
        """
        if len(name) > 0:
            self.values.append(name)
        else:
            self.values.append("記載なし")
