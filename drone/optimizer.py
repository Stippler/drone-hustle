


class Optimizer:

    def __init__(self, scheduler, confidence_estimator):
        pass

    def iterate(self):
        running = True
        while running:
            check = self.scheduler.check_constraints(constraints)
            constraints = self.confidence_estimator.get_constraints()