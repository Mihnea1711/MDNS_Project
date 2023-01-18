# class to store data (list of key=value -s) about a service
class TXT_RECORD:
    # should store pairs of key and values, including the length of the string
    # must not duplicate info already stored in srv!
    # only additional useful info

    def __init__(self):
        # txt records can't be empty ! ( not allowed in rfc's )
        self.list = ["key=value"]

    def __str__(self):
        toString = ""
        for string in self.list:
            toString += string + "\n"
        return toString

    def getList(self):
        return self.list

    # validate the update of the txt list
    def updateList(self, list_to_insert):
        flag = True
        message = ""
        undo_list = self.list
        list_to_insert = list(filter(lambda row: row != "", list_to_insert))

        self.list = []
        for pair in list_to_insert:
            # check if there is only 1 '=' sign
            words = pair.split("=")
            if len(words) != 2:
                flag = False
                message += "TXT Record pair should not contain more than 1 = sign!\n"
                break

            key = words[0].strip()
            value = words[1].strip()
            string = f"{key}={value}"

            self.list.append(string)

        if flag:
            message = "Values for TXT-Record look good.\n"
        else:
            self.list = undo_list

        return flag, message

