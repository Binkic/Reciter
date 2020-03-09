import json, zhon.hanzi, string

custom_punctuation = string.punctuation + zhon.hanzi.punctuation + ' '
custom_punctuation = set(custom_punctuation)

def judge_title(a, b) :
    _a = ''.join(ch for ch in a if ch not in custom_punctuation)
    _b = ''.join(ch for ch in b if ch not in custom_punctuation)
    return _a == _b

def process_comprehension(comprehension) :
    for i in universal_repositories :
        if judge_title(i["title"], comprehension["title"] ):

            if "source" not in i :
                try :
                    i["source"] = comprehension["source"]
                except KeyError :
                    pass

            if "author" not in i :
                try :
                    i["author"] = comprehension["author"]
                except KeyError :
                    pass

            single_record = {}
            single_record["content"] = comprehension["content"]
            single_record["answer"] = comprehension["answer"]

            try :
                comprehensions = i['comprehensions']
            except KeyError :
                i['comprehensions'] = []
                comprehensions = i['comprehensions']

            comprehensions.append(single_record)

            return True
    return False


normal_file = open("normal/poems.json", "rt", encoding='utf-8')
normal = json.loads(normal_file.read())
normal_file.close()

comprehensions_file = open("comprehensions/comprehensions.json", "rt", encoding='utf-8')
comprehensions = json.loads(comprehensions_file.read())
comprehensions_file.close()

universal = {}
universal_repositories = []
universal["$schema"] = "https://reciter.binkic.com/universal/schema.json"
universal["repositories"] = universal_repositories


for i in normal["poems"] :
    single_record = {}
    single_record["title"] = i["title"]
    single_record["normal"] = i["content"]
    try :
        single_record["source"] = i["source"]
    except KeyError :
        pass
    try :
        single_record["author"] = i["author"]
    except KeyError :
        pass

    
    # single_record["comprehensions"] = []
    universal_repositories.append(single_record)

for comprehension in comprehensions["comprehensions"] :
    if not process_comprehension(comprehension) :
        print(comprehension)

for i in range(0,len(universal_repositories)) :
    old = universal_repositories[i]
    new = {}

    for j in ["title", "author", "source", "normal", "comprehensions"] :
        try :
            new[j] = old[j]
        except KeyError :
            pass

    universal_repositories[i] = new

save = open("universal/universal.json", "w+", encoding='utf-8')
save.write( json.dumps(universal, indent = 4 , ensure_ascii = False ) )
save.close()




