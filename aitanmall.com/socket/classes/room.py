from classes.member import Member

class Room():
    def __init__(self, room_number:str = "000000"):
        if not isinstance(room_number, str):
            raise Exception("Room number must be string")
        if len(room_number) < 6:
            raise Exception("Room number need to be 6 or more")
        self.room_number = room_number
        self.members = []
        self.members_count = 0

    def __eq__(self, other):
        if not isinstance(other, Room):
            raise Exception("Room can only be compared to Room")
        return self.room_number == other.room_number

    def __lt__(self, other):
        if not isinstance(other, Room):
            raise Exception("Room can only be compared to Room")
        return self.room_number < other.room_number

    def __le__(self, other):
        if not isinstance(other, Room):
            raise Exception("Room can only be compared to Room")
        return self.room_number <= other.room_number

    def __gt__(self, other):
        if not isinstance(other, Room):
            raise Exception("Room can only be compared to Room")
        return self.room_number > other.room_number

    def __ge__(self, other):
        if not isinstance(other, Room):
            raise Exception("Room can only be compared to Room")
        return self.room_number >= other.room_number
    
    #accessor
    def get_room_number(self):
        return self.room_number

    def get_members(self, index=None):
        try:
            if index == None:
                return self.members
            elif isinstance(index, int):
                return self.members[index]
            else:
                raise Exception("Invalid index")
        except Exception as e:
            return e

    def get_members_count(self):
        return self.members_count
    
    #mutator
    def add_member(self, member):
        if not isinstance(member, Member):
            raise Exception("Member must be class Member")
        self.members.append(member)
    
    def remove_member(self, member:Member = None, index:int = None) -> Member:
        try:
            if isinstance(index, int):
                member_removed = self.members.pop(index)
                member_removed.kill_websocket()
                self.members_count -= 1
            elif member != None and index == None:
                member.kill_websocket()
                index_member = self.members.index(member)
                member_removed = self.members.pop(index_member)
                self.members_count -= 1
            else:
                member_removed = None

            return member_removed
        except Exception as e:
             return e
