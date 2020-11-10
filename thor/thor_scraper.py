from sys import exit
from copy import copy
# Thor simulator
import ai2thor.controller
# PARENT classes
from utils import KnowledgeSource, RoomType, Room, logout
from thor.config import thor_config
# GLOBALS
THOR = None


class Thor(KnowledgeSource):
    def __init__(self, name, config):
        KnowledgeSource.__init__(self, name, config)
        for room_type, room_type_ids in self.room_types_dict.items():
            self.room_types[room_type] = ThorRoomType(room_type, room_type_ids, config)


class ThorRoomType(RoomType):
    def __init__(self, room_type, ids, config):
        RoomType.__init__(self, room_type, ids)
        seeds = config["room_seeds"]
        for room_id in self.ids:
            for seed in seeds:
                if room_id not in self.rooms:
                    self.rooms[room_id] = [ThorRoom(room_type, room_id, seed, config["triple_rules"])]
                else:
                    self.rooms[room_id].append(ThorRoom(room_type, room_id, seed, config["triple_rules"]))


class ThorRoom(Room):
    def __init__(self, room_type, room_id, random_seed, rules):
        Room.__init__(self, room_type, room_id, random_seed)
        self.rules = rules

    def scrape(self):
        self.extend_ents(self.room_type)
        room_obj = collect_room_data(self.id, self.seed)
        for item in room_obj:
            object_type = item["objectType"].lower()+".o"
            self.extend_ents(object_type)
            # extracts state and action triples
            triples = []
            triples.extend(self.get_state_action_triples(object_type))
            # extracts material triples
            if item["salientMaterials"] is not None and item["salientMaterials"] != []:
                self.extend_rels("hasMat")
                for mat in item["salientMaterials"]:
                    mat_type = mat.lower()+".m"
                    self.extend_ents(mat_type)
                    triples.append((object_type, "hasMat", mat_type))
                    triples.extend(self.get_state_action_triples(object_type,mat))
            # extracts location triples
            if item["receptacle"]:
                container_obj_type = item["objectType"].lower() + ".l"
                self.extend_ents(container_obj_type)
                if item["receptacleObjectIds"] is not None and item["receptacleObjectIds"] != []:
                    for obj_id in item["receptacleObjectIds"]:
                        contained_obj_type = obj_id.split('|')[0].lower()+".o"
                        self.extend_ents(contained_obj_type)
                        rel = self.rules["receptacle_InOn"][container_obj_type]
                        self.extend_rels(rel)
                        triples.append((contained_obj_type, rel, container_obj_type))
                self.extend_rels("LocInRoom")
                triples.append((container_obj_type, "LocInRoom", self.room_type))
            else:
                self.extend_rels("ObjInRoom")
                triples.append((object_type, "ObjInRoom", self.room_type))
            # extracts operates on triples
            if self.rules["obj_OperatesOn"][object_type]:
                self.extend_rels("OperatesOn")
            for operated_object in self.rules["obj_OperatesOn"][object_type]:
                self.extend_ents(operated_object)
                triples.append((object_type,"OperatesOn",operated_object))

            self.triples.extend(triples)
        self.unique_triples.extend(list(set(copy(self.triples))))

    def get_state_action_triples(self, entity, material=None):
        actions = set()
        states = set()
        inverse_actions = set()
        inverse_states = set()
        triples = set()
        if material is not None:
            triple_ent = material.lower() + ".m"
            rel_begin = "Mat"
        else:
            triple_ent = entity
            rel_begin = "Obj"

        # gets action triples
        if self.rules["obj_canBe"][entity]:
            self.extend_rels(rel_begin+"CanBe")
        for action in self.rules["obj_canBe"][entity]:
            actions.add(action)
            triples.add((triple_ent,rel_begin+"CanBe",action))
        if self.rules["obj_usedTo"][entity]:
            self.extend_rels(rel_begin+"UsedTo")
        for action in self.rules["obj_usedTo"][entity]:
            actions.add(action)
            triples.add((triple_ent,rel_begin+"UsedTo",action))

        if material is None:
            for action in actions:
                if action in self.rules["action_inverseActionOf"]:
                    self.extend_rels("inverseActionOf")
                    for inverse_action in self.rules["action_inverseActionOf"][action]:
                        inverse_actions.add(inverse_action)
                        triples.add((action,"inverseActionOf",inverse_action))
            for action in actions:
                if action in self.rules["action_hasEffect"]:
                    self.extend_rels("hasEffect")
                    for state in self.rules["action_hasEffect"][action]:
                        states.add(state)
                        triples.add((action, "hasEffect", state))

        # gets state triples
        if self.rules["obj_hasState"][entity]:
            self.extend_rels(rel_begin+"hasState")
        for state in self.rules["obj_hasState"][entity]:
            states.add(state)
            triples.add((triple_ent, rel_begin+"hasState", state))

        if material is None:
            for state in states:
                if self.rules["state_inverseStateOf"][state]:
                    self.extend_rels("inverseStateOf")
                for inverse_state in self.rules["state_inverseStateOf"][state]:
                    inverse_states.add(inverse_state)
                    triples.add((state, "inverseStateOf", inverse_state))

        # extends ent with actions/states
        actions = actions.union(inverse_actions)
        states = states.union(inverse_states)
        for action in actions:
            self.extend_ents(action)
        for state in states:
            self.extend_ents(state)
        return list(triples)


def collect_room_data(room_id, random_seed):
    global THOR
    THOR.reset("FloorPlan" + str(room_id))
    THOR.step(dict(action="Initialize", gridSize=0.25))
    start_event = THOR.step(dict(action="InitialRandomSpawn", random_seed=random_seed))
    room_config = copy(start_event.metadata['objects'])
    return room_config


def setup_thor():
    global THOR
    try:
        THOR = ai2thor.controller.Controller(scene="FloorPlan30")
        logout("AI2Thor about to start.", "s")
        logout("AI2Thor started.", "s")
    except Exception as e:
        logout("Not able to launch AI2Thor. See below...", "f")
        logout(e, "f")
        exit()


def shutdown_thor():
    global THOR
    THOR.stop()


if __name__ == '__main__':
    setup_thor()
    thor_dataset = Thor("thor", thor_config)
    thor_dataset.scrape()
    thor_dataset.save()
    # uncomment line below to write to txt files in addition to the pickle file
    #thor_dataset.write()
    shutdown_thor()
    logout("Number of unique triples: "+str(len(thor_dataset.get_unique_triples())), "i")
    logout("Number of triples: " + str(len(thor_dataset.get_triples())), "i")
    logout("Number of entities: " + str(len(thor_dataset.get_ents())), "i")
    logout("Number of relations: " + str(len(thor_dataset.get_rels())), "i")
