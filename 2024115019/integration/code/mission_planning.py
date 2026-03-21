class Mission:
    def __init__(self, name, required_roles):
        self.name = name
        self.required_roles = required_roles
        self.assigned = False

class MissionPlanning:
    def __init__(self, registration):
        self.registration = registration
        self.missions = []

    def assign_mission(self, mission_name, required_roles, assigned_members=None):
        # assigned_members: dict mapping role -> member name
        if assigned_members is None:
            assigned_members = {}
        used_members = set()
        for role in required_roles:
            member_name = assigned_members.get(role)
            if not member_name:
                # Try to find any available member with this role not already used
                found = False
                for m in self.registration.members.values():
                    if m.role == role and m.name not in used_members:
                        used_members.add(m.name)
                        found = True
                        break
                if not found:
                    raise ValueError(f"No available crew member with role: {role}")
            else:
                member = self.registration.get_member(member_name)
                if not member or member.role != role or member.name in used_members:
                    raise ValueError(f"Invalid or duplicate member assignment for role: {role}")
                used_members.add(member.name)
        mission = Mission(mission_name, required_roles)
        mission.assigned = True
        self.missions.append(mission)
        return mission
