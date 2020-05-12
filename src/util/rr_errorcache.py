class error_reader(object):
    def __init__(self):
        self.errors = ""
        f = open("ERRORCACHE", "r")
        self.errors_len = 0
        f.close()
        # print("Initialized errors_len to ", self.errors_len)
        

    def read_errors(self):
        # open and read the file after the appending:
        f = open("ERRORCACHE", "r")
        # print(f.read())
        # print("Errors len:", self.errors_len)
        tmp_str = f.read()
        print("---")
        print(tmp_str[self.errors_len:])
        print("---")
        self.errors_len = len(tmp_str)
        f.close()


def write_error(ipt_str):
    f = open("ERRORCACHE", "a")
    f.write(ipt_str)
    f.close()

def flush_cache_file():
    f = open("ERRORCACHE", "w")
    f.write("")
    f.close()


er = error_reader()
write_error("error123\n")
er.read_errors()
write_error("error124\n")
er.read_errors()
write_error("error125\n")
er.read_errors()
write_error("error126\n")
er.read_errors()
flush_cache_file()

