class CrewMember:
    def __init__(self, name, role):
        self.name = name
        self.role = role

class Registration:
    def __init__(self):
        self.members = {}

    def register_member(self, name, role):
        if name in self.members:
            raise ValueError("Crew member already registered")
        self.members[name] = CrewMember(name, role)
        return self.members[name]

    def get_member(self, name):
        return self.members.get(name)
