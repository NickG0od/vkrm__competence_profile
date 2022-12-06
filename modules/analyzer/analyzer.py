import os
import argparse
import json
import jellyfish
import nltk
nltk.download('punkt')
nltk.download("stopwords")
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from nltk import FreqDist
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder


PUNCTUATION_CHARS = [' ', ',', '.', '...', '!', '?', '/', '\\', '(', ')', '-', '_', '+', '*', ':', '\'', '\"', '`', '—', '’']
AMOUNT_TO_SHOW = 200
N_BEST = 50 # number of bigrams to extract
CONFIDENCE_FACTOR = 2


def load_data(id, load_type="only_text"):
    data = None
    if id == None:
        print("> ID не обнаружен.")
        return None
    folder_name = f"./data/{id}"
    if not os.path.exists(folder_name):
        print("> Папка с таким ID не обнаружена.")
        return None
    data_file = None
    with open(f"{folder_name}/data.json", 'r', encoding='utf-8') as json_file:
        data_file = json.load(json_file)
    if load_type == "only_text" or load_type == "only_text_full":
        data = ""
    if load_type == "as_list":
        data = []
    for elem in data_file:
        if load_type == "only_text":
            data += f"{elem['description']}\n"
        if load_type == "only_text_full":
            data += f"{elem['description']}\n"
            data += f"{elem['description_full']}\n"
        if load_type == "as_list":
            data.append({'title': elem['title'], 'text': elem['description']})
    return data


def init(id = None):
    full_text = load_data(id)
    if not full_text:
        return None
    result = text_processing(full_text)
    return result


def text_processing(text):
    if text == "":
        print("> Текст на обработку пуст.")
        return False
    words = word_tokenize(text)
    stop_words_en = set(stopwords.words("english"))
    stop_words_ru = set(stopwords.words("russian"))
    filtered_words = []
    for word in words:
        if word.casefold() not in stop_words_en and word.casefold() not in stop_words_ru and word.casefold() not in PUNCTUATION_CHARS:
            filtered_words.append(word.casefold())
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
    unique_words = []
    for word in lemmatized_words:
        if word not in unique_words:
            unique_words.append(word)
    unique_words.sort()
    frequency_distribution = FreqDist(lemmatized_words)
    # print(f"{text}\n\n\n{words}\n\n\n{unique_words}")
    # print(frequency_distribution.most_common(AMOUNT_TO_SHOW))
    # frequency_distribution.plot(AMOUNT_TO_SHOW, cumulative=True)
    # collacation
    bm = BigramAssocMeasures()
    f = BigramCollocationFinder.from_words(lemmatized_words)
    # f.apply_freq_filter(5) # фильтр по частоте встречаемости
    raw_freq_ranking = [' '.join(i) for i in f.nbest(bm.raw_freq, N_BEST)]
    print(f"\n\n{raw_freq_ranking}\n\n")
    return {'words': unique_words, 'combinations': raw_freq_ranking, 'lemmatized_words': lemmatized_words}


def text_analysis(id = None, filter = None):
    if not id or not filter or not isinstance(filter, list):
        return False
    loaded_data = load_data(id, "as_list")
    if not loaded_data or len(loaded_data) <= 0:
        return False
    result = {}
    for elem in loaded_data:
        elem['lemmatized_words'] = []
        text_processing_res = text_processing(elem['text'])
        if text_processing_res:
            elem['lemmatized_words'] = text_processing_res['lemmatized_words']
    for filter_word in filter:
        result[filter_word] = 0
    for filter_word in filter:
        for elem in loaded_data:
            for word in elem['lemmatized_words']:
                if jellyfish.levenshtein_distance(filter_word, word) < CONFIDENCE_FACTOR:
                    result[filter_word] += 1
                    break
    print(result, len(loaded_data))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-id")
    parser.add_argument("-mode")
    args = parser.parse_args()
    if args.id:
        if args.mode == "analyze":
            text_analysis(args.id, ["test"])
        else:
            init(args.id)
    else:
        print("> ID не обнаружен.")
