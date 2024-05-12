import spacy


def generate_url(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    print(doc)

    for ent in doc.ents:
        # print(ent.__dir__())
        print(ent.text, ent.label_)


# generate_url("All articles about Bitcoin")
generate_url("All articles about Tesla from the last month, sorted by recent first")
generate_url("Top business headlines in the US right now")
# generate_url("Top headlines from TechCrunch right now")
