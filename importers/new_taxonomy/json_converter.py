import json


def concept_to_taxonomy(values):
    json_dict = {}
    for value in values:
        json_dict[value["concept_id_str"]] = {}
        json_dict[value["concept_id_str"]]["legacyId"] = value["id"]
        json_dict[value["concept_id_str"]]["type"] = value["type"]
        json_dict[value["concept_id_str"]]["label"] = value["label"]
    print(len(values))
    print(len(json_dict))
    with open("concept_to_taxonomy.json", "w") as fout:
        json.dump(json_dict, fout,)


def taxonomy_to_concept(values):
    py_dict = {}
    for value in values:
        py_dict[value["type"]] = {}
        py_dict[value["type"]][value["id"]] = {}
        py_dict[value["type"]][value["id"]]["conceptId"] = value["concept_id_str"]
        py_dict[value["type"]][value["id"]]["legacyId"] = value["id"]
        py_dict[value["type"]][value["id"]]["preferredTerm"] = value["label"]
        py_dict[value["type"]][value["id"]]["type"] = value["type"]
    print(len(values))
    print(len(py_dict))
    with open("taxonomy_to_concept.json", "w") as fout:
        json.dump(py_dict, fout)


def unpickle_json(file_name):
    with open(file_name, "r") as fin:
        data = json.load(fin)
        for k, v in data.items():
            print(k, v)
