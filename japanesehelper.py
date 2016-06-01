import csv


class JapaneseHelper():
    def __init__(self):
        self.loadcsv()

        self.tatoeba_sentence_limit = 1

    def loadcsv(self):
        f = open('jpn_indices_edited.csv','r',encoding='utf-8')
        reader = csv.reader(f,dialect=csv.excel_tab)
        self.links = {}
        for row in reader:
            self.links[row[0]] = row[1]
        f.close()

        f = open('sentences_detailed_edited.csv', 'r', encoding='utf-8')
        reader = csv.reader(f,dialect=csv.excel_tab)
        self.sentences = {}
        for row in reader:
            self.sentences[row[0]] = row[2]
        f.close()



    def tatoeba(self,content):
        if len(content['message']) <= 9:
            content['message'] = 'Use $tatoeba <Japanese word/phrase>.'
            return content
        if content['private_messaged']:
            new_line = '\r\nPRIVMSG %s :' %(content['name'])
        else:
            new_line = '\r\nPRIVMSG %s :' %(content['channel'])
        keyword = content['message'][9:]
        
        jap_sentences = []

        for a in self.sentences.keys():
            if keyword in self.sentences[a]:
                if a in self.links.keys():
                    if self.links[a] in self.sentences.keys():
                        jap_sentences.append([self.sentences[a],self.sentences[self.links[a]]])
                    else:
                        jap_sentences.append([self.sentences[a],None])
                else:
                    jap_sentences.append([self.sentences[a],None])
            if len(jap_sentences) >= self.tatoeba_sentence_limit:
                break
        if len(jap_sentences) == 0:
            content['message'] = 'No results found.'
            return content
        if len(jap_sentences) > self.tatoeba_sentence_limit:
            jap_sentences = jap_sentences[:self.tatoeba_sentence_limit]
        
        content['message'] = '%d result(s) generated.' %(len(jap_sentences))
        for a in jap_sentences:
            content['message'] += new_line + a[0] + new_line + str(a[1])
        return content

    #This method is deprecated
    def tatoeba1(self, content):
        if len(content['message']) <= 9:
            content['message'] = 'Use $tatoeba <Japanese word/phrase>.'
            return content
        if content['private_messaged']:
            new_line = '\r\nPRIVMSG %s :' %(content['name'])
        else:
            new_line = '\r\nPRIVMSG %s :' %(content['channel'])
        keyword = content['message'][9:]
        
        jap_indices = []
        translation_indices = []
        jap_sentences = []
        translation = []

        self.sentences.seek(0)
        for row in self.sentence_reader:
            if keyword in row[2]:
                jap_indices.append(row[0])
                jap_sentences.append(row[2])
                if len(jap_indices) >= self.tatoeba_sentence_limit:
                    break

        if len(jap_indices) == 0:
            content['message'] = 'No results found.'
            return content

        for index in jap_indices:
            found = False
            self.indices.seek(0)
            for row in self.indices_reader:
                if row[0] == index:
                    translation_indices.append(row[1])
                    found = True
                    break
            if not found:
                translation_indices.append(None)

        for index in translation_indices:
            if index == None:
                translation.append(None)
            else:
                self.sentences.seek(0)
                found = False
                for row in self.sentence_reader:
                    if row[0] == index:
                        translation.append(row[2])
                        found = True
                if not found:
                    translation.append(None)

        content['message'] = '%d result(s) generated.' %(len(jap_indices))
        for raw_text,translation_text in zip(jap_sentences,translation):
            content['message'] += new_line + raw_text + new_line + str(translation_text)
        return content

