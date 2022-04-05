import pickle

chomp = "Users\paolo\OneDrive\Desktop\Page-Rank_Algorithm\Objects"

# Save an object of the class graph locally
def save(filename, object, mode):
    new_chomp = chomp + "\Twitter\\" if mode == "twitter" else chomp + "\PubMed\\"
    try:
        file_to_store = open(new_chomp + filename + ".pickle", "wb")
        pickle.dump(object, file_to_store)

        file_to_store.close()

    except Exception as ex:
        print("Error during storing data (Possibly unsupported):", ex)

# Load an object of the class graph locally
def load(filename, mode):
    new_chomp = chomp + "\Twitter\\" if mode == "twitter" else chomp + "\PubMed\\"
    try:
        file_to_read = open(new_chomp + filename + ".pickle", "rb")
        loaded_object = pickle.load(file_to_read)

        file_to_read.close()
        return loaded_object

    except Exception as ex:
        print("Error during loading data:", ex)
