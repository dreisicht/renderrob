import bpy
import time


def inexclude_collection(collection_names, exclude, parent=""):
    # check if first function being called first time
    if parent == "":
        counter = 0
        for name in collection_names:
            if name == "":
                collection_names.pop(counter)
            counter += 1
        parent_collection = bpy.data.scenes[0].view_layers[0].layer_collection
        # if function being called first time, reset number of changed
    else:
        parent_collection = parent

    # iterate through immediate children of collection
    for collection in parent_collection.children:
        # check name
        if collection.name in collection_names:
            collection.exclude = exclude
            collection_names.pop(collection_names.index(collection.name))
        # check if has children
        if len(collection.children) > 0:
            inexclude_collection(
                collection_names, exclude, parent=collection)
        else:
            continue
    if parent == "" and len(collection_names) > 0:
        print("ERROR: Couldn't find collection {}!".format(
            " and ".join(collection_names)))
        time.sleep(10)


activate_cols1 = "cameras, objects 1, lights 1".replace(", ", ",").split(",")
activate_cols2 = "cameras, objects 1, lights 1, nonexisting collection, ,  ".replace(
    ", ", ",").split(",")
deactivate_cols1 = "cameras 1, objects 1 1, lights 1 1".replace(
    ", ", ",").split(",")
deactivate_cols2 = "cameras 1, objects 1 1, lights 1 1, nonexisting collection, asdf collection".replace(
    ", ", ",").split(",")

# inexclude_collection(activate_cols1, False)
inexclude_collection(activate_cols2, False)
# inexclude_collection(deactivate_cols1, True)
inexclude_collection(deactivate_cols2, True)
