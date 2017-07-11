"""
https://mesosphere.com/careers/challenges/distributed-applications/?submitter=dhurng@gmail.com

Querying the state of the elevators (what floor are they on and where they are going),
receiving an update about the status of an elevator,
receiving a pickup request,
time-stepping the simulation.
"""


def main():
    a = Elevator(0, "Up")
    b = Elevator(4, "Down")
    c = Elevator(10, "Down")
    d = Elevator()

    a.add_destination(1)
    a.add_destination(3)
    a.add_destination(6)
    a.add_destination(7)

    b.add_destination(0)
    b.add_destination(2)

    c.add_destination(2)
    c.add_destination(5)
    c.add_destination(10)

    # d is empty and idle

    ecs = ElevatorControl()
    ecs.add_elevator(a)
    ecs.add_elevator(b)
    ecs.add_elevator(c)
    ecs.add_elevator(d)

    print "*" * 20, "Status", "*" * 20

    print ecs.status()

    print "*" * 20, "Update", "*" * 20

    for i in range(0, 4):
        print "Update of elevator id-{} = {}".format(i, ecs.update(i))

    print "*" * 20, "Pickup", "*" * 20

    ecs.pickup(0, 5)
    print ecs.status()
    ecs.pickup(9, 0)
    print ecs.status()
    ecs.pickup(3, 10)
    print ecs.status()

    print "*" * 20, "Step", "*" * 20

    ecs.step()
    print ecs.status()
    ecs.step()
    print ecs.status()
    ecs.step()
    print ecs.status()
    ecs.step()
    print ecs.status()
    ecs.step()
    print ecs.status()

class Elevator(object):
    def __init__(self, curr_floor=0, direction="Idle"):
        self.curr_floor = curr_floor
        self.direction = direction
        self.destinations = []
        self.pending = []

    def add_destination(self, trgt_floor):
        """
        adds new target floor to the destination list
        :param trgt_floor: int
        :return: none
        """
        if trgt_floor > self.curr_floor:
            self.destinations.append(trgt_floor)
            self.destinations = sorted(self.destinations)
        elif trgt_floor < self.curr_floor:
            self.destinations.append(trgt_floor)
            self.destinations = sorted(self.destinations, reverse=True)
        else:
            print "Same floor"

    def check_capacity(self):
        return len(self.destinations)

    def __str__(self):
        return "Elevator is on floor: {} and going {}".format(self.curr_floor, self.destinations)

    def __repr__(self):
        return "floor:{} = dest:{} = dir:{}".format(self.curr_floor, self.destinations, self.direction)

class ElevatorControl(object):
    def __init__(self):
        self.master = []
        self.has_idle = 0
        self.threshold_per_el = 4

    def status(self):
        """
        Querying the state of the elevators (what floor are they on and where they are going)
        :param elevator_id: int 
        :return: Tuple(Elevator.curr_floor, Elevator.direction)
        """
        for el in self.master:
            if el.direction == "Idle":
                self.has_idle += 1
        return self.master

    def update(self,  elevator_id):
        """
        receiving an update about the status of an elevator
        :return: list[elevators]
        """
        return self.master[elevator_id]

    def pickup(self, curr_floor, going=0):
        """
        receiving a pickup request
        :param curr_floor: int
        :param going: int
        :return: None
        """
        if curr_floor < going:
            dir = "Up"
        elif curr_floor > going:
            dir = "Down"
        else:
            dir = "Idle"

        if self.has_idle > 0:
            for i, el in enumerate(self.master):
                if el.direction == "Idle":
                    if el.curr_floor == curr_floor:
                        el.add_destination(going)
                    else:
                        el.add_destination(curr_floor)
                        el.pending.append(going)
                    el.direction = dir
                    self.has_idle -= 1
                    print "Elevator id-{} is already at f{} and going to f{}".format(i, curr_floor, going)
                    return

                """
                add pending if the elevator is going the opposite direction of dir
                
                what if all are at threshold
                """
        else:
            for i, el in enumerate(self.master):
                cap = el.check_capacity()
                if el.direction == "Up" and el.curr_floor < curr_floor and cap < self.threshold_per_el:
                    el.add_destination(curr_floor)
                    if dir == "Up":
                        el.add_destination(going)
                    else:
                        el.pending.append(going)
                    print "Elevator id-{} is picking up at f{} and going to f{}".format(i, curr_floor, going)
                    return
                elif el.direction == "Down" and el.curr_floor > curr_floor and cap < self.threshold_per_el:
                    el.add_destination(curr_floor)
                    if dir == "Down":
                        el.add_destination(going)
                    else:
                        el.pending.append(going)
                    print "Elevator id-{} is picking up at f{} and going to f{}".format(i, curr_floor, going)
                    return

    def step(self):
        """
        time-stepping the simulation
        :return: None
        """
        for i, el in enumerate(self.master):
            cap = el.check_capacity()
            if cap == 0 and len(el.pending) != 0:
                el.destinations, el.pending = el.pending, el.destinations
            elif cap == 0 and len(el.pending) == 0:
                el.direction = "Idle"
                continue
            el.curr_floor = el.destinations[0]
            del el.destinations[0]


    def add_elevator(self, elevator):
        self.master.append(elevator)

if __name__ == '__main__':
    main()