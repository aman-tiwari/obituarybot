import twitter
import nltk
import wikipedia as w
import random
import re

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def unparse(sentence):
    words = [token[0] for token in sentence]
    for i, word in enumerate(words):
        if word == ',' or word == ':':
            words[i - 1] += word
            del words[i]
    words = " ".join(words)
    if words[-1] == '.':
        words = words[:-1]
    return words

def preprocess_sentences(sentences):
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def rhyme(inp, level):
     entries = nltk.corpus.cmudict.entries()
     syllables = [(word, syl) for word, syl in entries if word == inp]
     rhymes = []
     for (word, syllable) in syllables:
             rhymes += [word for word, pron in entries if pron[-level:] == syllable[-level:]]
     return set(rhymes)

def np_chunk(sentence):
    grammar = nltk.RegexpParser("""NP:
                                  {<.*>+}
                                  }<CC>{""")

    result = grammar.parse(sentence)
    return result

def get_rhymes(target, sentences, level = 2):
    print target[-1][0]
    rhymes = rhyme(target[-1][0], level)
    result = []
    for sentence in sentences[1:]:
        if len(sentence) > 1 and sentence[-2][0] in rhymes and sentence[-2][0] != target:
            result.append(sentence)
    if len(result) > 0:
        return result
    else:
        rhymes = rhyme(target[-1][0], level-1)
        result = []
        for sentence in sentences[1:]:
            if len(sentence) > 1 and sentence[-2][0] in rhymes and sentence[-2][0] != target:
                result.append(sentence)
        return result


def get_poem(names):
    for name in names:
        try:
            text = w.page(name).content
        except w.exceptions.PageError:
            continue
        raw_sentences = nltk.sent_tokenize(text)
        sentences = preprocess_sentences(raw_sentences)
        first = np_chunk(sentences[0])[0]
        if first[-1][0] == '.':
            first = first[:-1]
        rhymes = get_rhymes(first, sentences)
        if len(rhymes) == 0:
            continue
        rhymes.sort(key=len)
        first = unparse(first)
        first = first.replace(' is ', ' was ')
        poem =  first + "\n" + unparse(rhymes[0]) + "\n" + "They died"
        poem = re.sub('\(([^)]+)\)', '', poem)
        poem = re.sub(' +', ' ', poem)
        if len(poem) <= 140:
            return poem
        elif len(poem) <= 149:
            poem = poem[:-10]
            return poem
        else:
            print "too long"
            print poem
            continue
    else:
        return None

api  = twitter.Api(consumer_key='',
                   consumer_secret='',
                   access_token_key='',
                   access_token_secret='')

def post_tweet(tweet):
    print tweet
    try:
        status = api.PostUpdate(tweet)
        print status
    except twitter.error.TwitterError:
        print twitter.error.TwitterError
        pass

def create_obit(possible_people):
    return get_poem(possible_people)

def random_death_list():
    year = random.randint(1987, 2015)
    if year > 2003:
        return "Deaths in " + random.choice(months) + " " + str(year)
    else:
        return "Deaths in " + str(year)

def get_people(n = 15):
    if n > 25:
        people = []
        for i in n // 25:
            people.extend(get_people(25))
        return people
    death_list = random_death_list()
    links = w.page(death_list).links
    content = w.page(death_list).content
    people = []
    random.shuffle(links)
    for person in links:
        loc = content.find(person)
        if loc > 0 and content[loc:loc + len(person) + 1][-1] == ',':
            people.append(person)
            if len(people) > n:
                return people

def main():
    people = get_people(25)
    try:
        obit = create_obit(people)
    except:
        obit = create_obit(people)
    if obit == None:
        main()
    else:
        post_tweet(obit)

while True:
    main()
