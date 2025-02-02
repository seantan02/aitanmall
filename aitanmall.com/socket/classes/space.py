from classes.room import Room
from helper import sorter
from typing import List
from math import floor

class Space():
    existing_space = []
    #constructor
    def __init__(self, name:str):
        if not isinstance(name,str):
            raise Exception("Name of space must be string")
        if name in Space.existing_space:
            raise Exception("Space already exist")
        self.space_name = name
        self.environment = []
        self.object_count = 0

    #accessor
    def get_name(self):
        return self.space_name
    
    def get_object_count(self):
        return self.object_count
        
    def get_environment(self) -> List[Room]:
        return self.environment
    
    def get_room(self, room_number:str):
        to_find = room_number
        found = None
        temp_environment = self.environment
        while True:
            midpoint = len(temp_environment)//2
            room = temp_environment[midpoint]
            if len(temp_environment)==1:
                if room.get_room_number() == to_find:
                    found = room
                return found
            if room.get_room_number() > to_find:
                temp_environment = temp_environment[0:midpoint]
            elif room.get_room_number() < to_find:
                temp_environment = temp_environment[midpoint+1:]
            if room.get_room_number() == to_find:
                found = room
                return found
            
    
    #mutator
    def create_room(self, room:Room):
        if not isinstance(room, Room):
            raise Exception("Only room can be added to environment")
        self.environment.append(room)
        sorter.mergeSort(self.environment, 0, self.object_count)
        self.object_count += 1

    def remove_room(self, room_to_find:Room):
        #find the midpoint, see which side is what we want
        if not isinstance(room, Room):
            raise Exception("Room has to be class Room")
        
        found = None
        temp_environment = self.environment
        while True:
            midpoint = len(temp_environment)//2
            room = temp_environment[midpoint]
            if len(temp_environment)==1:
                if room == room_to_find:
                    found = self.environment.pop(midpoint)
                    self.object_count -= 1
                return found
            if room > room_to_find:
                temp_environment = temp_environment[0:midpoint]
            elif room < room_to_find:
                temp_environment = temp_environment[midpoint+1:]

            if room == room_to_find:
                found = self.environment.pop(midpoint)
                self.object_count -= 1
                return found
