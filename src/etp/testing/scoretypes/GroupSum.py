from etp.testing.scoretypes.ScoreType import ScoreTypeGroup


class GroupSum(ScoreTypeGroup):
    """The score of a submission is the sum of group scores,
    and each group score is the sum of testcase scores in the group.

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
        return sum(outcomes) / len(outcomes)