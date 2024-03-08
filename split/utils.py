from constants import *
from PyQt5.QtGui import QTextCharFormat, QTextCursor


class Utility():
    def __init__(self, big_brother):
        self.bb = big_brother
        
        self.houseguests = self.bb.houseguests
        
        self.chosen_color = self.bb.chosen_color
        self.hoh_color = self.bb.hoh_color
        self.noms_color = self.bb.noms_color
        self.veto_color = self.bb.veto_color
        self.evicted_color = self.bb.evicted_color
        self.no_color = self.bb.no_color
        self.imp_color = self.bb.imp_color
        self.name_color = self.bb.name_color
        self.evict_statement_color = self.bb.evict_statement_color
        self.formatting = self.bb.formatting
        self.text_box = self.bb.text_box
        self.set_selves()
        
    def print_text(self, text, nl=True):
        self.make_formatting()
        default_char_format = QTextCharFormat()
        cursor = self.text_box.textCursor()
        cursor.movePosition(QTextCursor.End)

        lines = text.split("\n")
        for line in lines:
            formatted_indices = []
            formatted_phrases = []
            for phrase, format in self.formatting.items():
                if phrase in line:
                    start = line.index(phrase)
                    end = start + len(phrase)
                    formatted_indices.append((start, end))
                    formatted_phrases.append((phrase, format))

            if formatted_indices:
                last_end = 0
                for start, end, (phrase, format) in sorted(zip(
                    [i[0] for i in formatted_indices],
                    [i[1] for i in formatted_indices],
                    formatted_phrases
                )):
                    cursor.insertText(line[last_end:start], default_char_format)
                    char_format = QTextCharFormat()
                    char_format.setForeground(format)
                    cursor.insertText(phrase, char_format)
                    last_end = end
                cursor.insertText(line[last_end:], default_char_format)
            else:
                for word in line.split():
                    name = self.get_name_with_format(word)
                    if name:
                        char_format = QTextCharFormat()
                        char_format.setForeground(name[1])
                        cursor.insertText(name[0], char_format)
                        cursor.insertText(" ", default_char_format)
                    else:
                        cursor.insertText(word, default_char_format)
                        cursor.insertText(" ", default_char_format)
            cursor.insertText("\n", default_char_format)

        if nl:
            cursor.insertText("\n", default_char_format)

        self.text_box.setTextCursor(cursor)
            
    def make_formatting(self):
        self.set_selves()
        for hg in self.houseguests:
            n = hg.name
            self.formatting[n] = self.name_color  # Reset to default text color
            if self.HOH is not None and self.HOH.name == n:
                print(f"Setting {n} to hoh_color")
                self.formatting[n] = self.hoh_color
            if self.veto_winner is not None and self.veto_winner.name == n:
                print(f"Setting {n} to veto_color")
                self.formatting[n] = self.veto_color
            if self.nominees and self.formatting[n] != self.veto_color and self.formatting[n] != self.evicted_color:
                for p in self.nominees:
                    if p.name == n:
                        print(f"Setting {n} to nom_color")
                        self.formatting[n] = self.noms_color
            if self.evicted is not None and self.evicted.name == n:
                print(f"Setting {n} to evicted_color")
                self.formatting[n] = self.evicted_color
                
    def set_selves(self):
        self.houseguests = self.bb.houseguests
        self.HOH = self.bb.HOH  
        self.veto_winner = self.bb.veto_winner
        self.nominees = self.bb.nominees
        self.evicted = self.bb.evicted
        self.alliances = self.bb.alliances
        self.debug_impressions = self.bb.debug_impressions
                    
    def get_name_with_format(self, char):
        for name, format in self.formatting.items():
            print(name, format, self.no_color)
            if name.startswith(char) and format is not self.no_color:
                return name, format
        return None