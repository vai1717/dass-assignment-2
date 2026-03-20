class CrewManagement:
    def __init__(self, registration):
        self.registration = registration
        self.skills = {}  # name -> skill dict

    def assign_role(self, name, role):
        member = self.registration.get_member(name)
        if not member:
            raise ValueError("Crew member not registered")
        member.role = role

    def set_skill(self, name, skill, level):
        if name not in self.skills:
            self.skills[name] = {}
        self.skills[name][skill] = level

    def get_skills(self, name):
        return self.skills.get(name, {})
