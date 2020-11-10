import os
from copy import copy
from pickle import dump


class KnowledgeSource:
    def __init__(self, name, config):
        self.name = name
        self.room_types_dict = config["room_types"]
        self.room_types = {}
        self.ents = []
        self.rels = []
        self.triples = []
        self.unique_triples = []

    def scrape(self):
        for room_type, room_type_ids in self.room_types_dict.items():
            logout("Scraping '" + room_type + "' rooms", "d")
            self.room_types[room_type].scrape()
        self.scrape_ents()
        self.scrape_rels()
        self.scrape_triples()
        self.scrape_unique_triples()

    def save(self):
        logout("Storing Thor dataset object", "d")
        source_fp = os.path.dirname(os.path.realpath(__file__))+"/"+self.name+"/rooms"
        if not os.path.exists(source_fp):
            os.makedirs(source_fp)

        dataset_fp = source_fp + "/" + self.name + ".pkl"
        with open(dataset_fp, 'wb') as f:
            dump(self, f)
        self.save_rels(source_fp)
        self.save_ents(source_fp)

    def write(self):
        logout("Writing all loaded rooms", "d")
        source_fp = os.path.dirname(os.path.realpath(__file__))+"/"+self.name+"/rooms"
        if not os.path.exists(source_fp):
            os.makedirs(source_fp)
        for room_type, room_type_ids in self.room_types_dict.items():
            self.room_types[room_type].write(source_fp)
        self.save_rels(source_fp)
        self.save_ents(source_fp)

    def save_ents(self, fp):
        with open(fp+"/entities.txt", "w") as f:
            f.write(str(len(self.get_ents())) + "\n")
            for ent_idx in range(len(self.get_ents())):
                ent = self.get_ents()[ent_idx]
                f.write(ent + "\t" + str(ent_idx) + "\n")

    def save_rels(self, fp):
        with open(fp+"/relations.txt", "w") as f:
            f.write(str(len(self.get_rels())) + "\n")
            for rel_idx in range(len(self.get_rels())):
                rel = self.get_rels()[rel_idx]
                f.write(rel + "\t" + str(rel_idx) + "\n")

    def scrape_ents(self):
        [self.ents.extend(room_type_obj.get_ents()) for room_type_obj in self.room_types.values()]
        self.ents = list(set(self.ents))

    def scrape_rels(self):
        [self.rels.extend(room_type_obj.get_rels()) for room_type_obj in self.room_types.values()]
        self.rels = list(set(self.rels))

    def scrape_triples(self):
        [self.triples.extend(room_type_obj.get_triples()) for room_type_obj in self.room_types.values()]

    def scrape_unique_triples(self):
        if not self.triples:
            self.scrape_triples()
        self.unique_triples = list(set(copy(self.triples)))

    def get_ents(self):
        self.ents.sort()
        return self.ents

    def get_rels(self):
        self.rels.sort()
        return self.rels

    def get_triples(self):
        return self.triples

    def get_unique_triples(self):
        return self.unique_triples


class RoomType:
    def __init__(self, room_type, ids):
        self.type = room_type
        self.ids = ids
        self.rooms = {}
        self.ents = []
        self.rels = []
        self.triples = []
        self.unique_triples = []

    def scrape(self):
        for room_id, room in self.rooms.items():
            for room_config in room:
                room_config.scrape()
        self.scrape_ents()
        self.scrape_rels()
        self.scrape_triples()
        self.scrape_unique_triples()

    def scrape_ents(self):
        for room_id, room in self.rooms.items():
            for room_config in room:
                self.ents.extend(room_config.get_ents())
        self.ents = list(set(self.ents))

    def scrape_rels(self):
        for room_id, room in self.rooms.items():
            for room_config in room:
                self.rels.extend(room_config.get_rels())
        self.rels = list(set(self.rels))

    def scrape_triples(self):
        for room_id, room in self.rooms.items():
            for room_config in room:
                self.triples.extend(room_config.get_triples())

    def scrape_unique_triples(self):
        if not self.triples:
            self.scrape_triples()
        self.unique_triples = list(set(copy(self.triples)))

    def get_ents(self):
        self.ents.sort()
        return self.ents

    def get_rels(self):
        self.rels.sort()
        return self.rels

    def get_triples(self):
        return self.triples

    def get_unique_triples(self):
        return self.unique_triples

    def save(self, fp):
        room_type_fp = fp + '/' + self.type
        if not os.path.exists(room_type_fp):
            os.makedirs(room_type_fp)
        for room_id, room in self.rooms.items():
            for room_config in room:
                room_config.save(room_type_fp)

    def write(self, fp):
        room_type_fp = fp + '/' + self.type
        if not os.path.exists(room_type_fp):
            os.makedirs(room_type_fp)
        for room_id, room in self.rooms.items():
            for room_config in room:
                room_config.write(room_type_fp)


class Room:
    def __init__(self, room_type, room_id, random_seed):
        self.room_type = room_type
        self.id = room_id
        self.seed = random_seed
        self.ents = []
        self.rels = []
        self.triples = []
        self.unique_triples = []

    def scrape(self):
        raise NotImplementedError

    def get_ents(self):
        self.ents.sort()
        return self.ents

    def get_rels(self):
        self.rels.sort()
        return self.rels

    def get_triples(self):
        return self.triples

    def get_unique_triples(self):
        return self.unique_triples

    def extend_ents(self, candidate):
        if candidate not in self.ents:
            self.ents.append(candidate)

    def extend_rels(self, candidate):
        if candidate not in self.rels:
            self.rels.append(candidate)

    def save(self, fp):
        room_fp = fp + "/" + str(self.id) + "_" + str(self.seed) + ".pkl"
        with open(room_fp, 'wb') as f:
            dump(self.__dict__, f)

    def write(self, fp):
        room_fp = fp + "/" + str(self.id) + "_" + str(self.seed) + ".csv"
        with open(room_fp, 'w') as f:
            for triple in self.triples:
                head, rel, tail = triple
                f.write(str(head)+","+str(rel)+","+str(tail)+"\n")


type2color = {
    's': ' \033[95mSuccess:\033[00m {}',
    'i': ' \033[94mInfo:\033[00m {}',
    'd': ' \033[92mDebug:\033[00m {}',
    'w': ' \033[93mWarning:\033[00m {}',
    'e': ' \033[91mError:\033[00m {}',
    'f': ' \033[4m\033[1m\033[91mFatal Error:\033[00m {}'
}


def logout(msg, p_type=''):
    """ Provides coloring debug printing to terminal """
    if not p_type.lower() in type2color:
        start = type2color['d']
    else:
        start = type2color[p_type.lower()]
    print(start.format(msg))
