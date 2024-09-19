from etp.testing.scoretypes.GroupSum import GroupSum


class GroupSumCheck(GroupSum):
    """The score of a submission is the sum of group scores,
    and each group score is the sum of testcase scores in the group,
    except when any testcase scores is negative, the total for the
    whole group is zero.
    """

    def reduce(self, outcomes, parameter):
        """See ScoreTypeGroup."""
        if min(outcomes) < 0: return 0.0
        return sum(outcomes) / len(outcomes)