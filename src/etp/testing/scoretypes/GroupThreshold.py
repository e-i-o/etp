from etp.testing.scoretypes.ScoreType import ScoreTypeGroup


class GroupThreshold(ScoreTypeGroup):
    """The score of a submission is the sum of: the multiplier of the
    range if all outcomes are between 0.0 (excluded) and the
    threshold, or 0.0 otherwise. Zero is excluded as it is a special
    value used by many task types, for example when the contestant
    solution times out.

    Parameters are [[m, t, T], ... ] (see ScoreTypeGroup), where T is
    the threshold for the group.

    """

    def get_public_outcome(self, outcome, parameter):
        """See ScoreTypeGroup."""
        threshold = parameter[2]
        if 0.0 < outcome <= threshold:
            return "Correct"
        else:
            return "Not correct"

    def reduce(self, outcomes, parameter):
        """See ScoreTypeGroup."""
        threshold = parameter[2]
        if all(0 < outcome <= threshold for outcome in outcomes):
            return 1.0
        else:
            return 0.0
