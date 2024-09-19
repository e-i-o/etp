from etp.testing.scoretypes.ScoreType import ScoreTypeGroup


class GroupMin(ScoreTypeGroup):
    """The score of a submission is the sum of the product of the
    minimum of the ranges with the multiplier of that range.

    Parameters are [[m, t], ... ] (see ScoreTypeGroup).

    """

    def get_public_outcome(self, outcome, unused_parameter):
        """See ScoreTypeGroup."""
        if outcome <= 0.0:
            return "Not correct"
        elif outcome >= 1.0:
            return "Correct"
        else:
            return "Partially correct"

    def reduce(self, outcomes, unused_parameter):
        """See ScoreTypeGroup."""
        return min(outcomes)