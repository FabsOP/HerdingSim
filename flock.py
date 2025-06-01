import numpy as np
from boid import behaviours

class Flock:
    def __init__(self,species, members):
        self.members = members
        self.species = species
        self.size = len(members)
        
        for member in members:
            member.setFlock(self)
        
    def add_member(self, boid):
        """Add a boid to the flock."""
        if self.size < behaviours[self.species]["herd-size"][4]:
            self.members.append(boid)
            self.size +=1
            boid.setFlock(self)
    
    def remove_member(self, boid):
        """Remove a boid from the flock."""
        if boid in self.members:
            self.members.remove(boid)
            self.size -= 1
            boid.setFlock(Flock(species=self.species, members=[boid]))
    
    def limitFlockSize(self):
        maxHerdSize = behaviours[self.species]["herd-size"][4]
        if self.size > maxHerdSize:
            staying = self.members[:maxHerdSize]
            leaving = self.members[maxHerdSize:]
            
            for animal in leaving:
                self.remove_member(animal)
                
            for animal in staying:
                animal.setFlock(self)
            
            
        
    
        
        
        
    
    