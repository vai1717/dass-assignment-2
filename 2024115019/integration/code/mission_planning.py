class Mission:
    def __init__(self, name, required_roles):
        self.name = name
        self.required_roles = required_roles
        self.assigned = False

class MissionPlanning:
    def __init__(self, registration):
        self.registration = registration
        self.missions = []

    def assign_mission(self, mission_name, required_roles):
        # Check if all required roles are available
        for role in required_roles:
            if not any(m.role == role for m in self.registration.members.values()):
                raise ValueError(f"No crew member with role: {role}")
        mission = Mission(mission_name, required_roles)
        mission.assigned = True
        self.missions.append(mission)
        return mission
