from abc import ABCMeta, abstractmethod, ABC
from typing import Tuple, Any, List

from etp.config.genfile import Genfile
from etp.testing.scoretypes.adapters import SubmissionResult


class ScoreType(metaclass=ABCMeta):
    """Base class for all score types, that must implement all methods
    defined here.

    """

    def __init__(self, genfile: Genfile):
        """Initializer.

        parameters (object): format is specified in the subclasses.
        """
        self.parameters = []
        for group in genfile.groups:
            self.parameters.append([group.points, len(group.tests)] + group.parameters)
        self.n_input = sum([len(group.tests) for group in genfile.groups])

        # Preload the maximum possible scores.
        try:
            self.max_score = self.max_scores()
        except Exception as e:
            raise ValueError(
                "Unable to instantiate score type (probably due to invalid "
                "values for the score type parameters): %s." % e)

    @abstractmethod
    def max_scores(self) -> float:
        """Returns the maximum score that one could aim to in this
        problem. Also return the maximum score from the point of view
        of a user that did not play the token. And the headers of the
        columns showing extra information (e.g. subtasks) in RWS.
        Depend on the subclass.

        return float: maximum score and maximum score with only public
        testcases; ranking headers.

        """
        pass

    @abstractmethod
    def compute_score(self, unused_submission_result) -> Tuple[float, Any]:
        """Computes a score of a single submission.

        unused_submission_result (SubmissionResult): the submission
            result of which we want the score

        return (float, object): respectively: the
            score, an opaque JSON-like data structure with additional
            information (e.g. testcases' and subtasks' score)

        """
        pass


class ScoreTypeAlone(ScoreType, ABC):
    """Intermediate class to manage tasks where the score of a
    submission depends only on the submission itself and not on the
    other submissions' outcome. Remains to implement compute_score to
    obtain the score of a single submission and max_scores.

    """
    pass


class ScoreTypeGroup(ScoreTypeAlone):
    """Intermediate class to manage tasks whose testcases are
    subdivided in groups (or subtasks). The score type parameters must
    be in the form [[m, t, ...], [...], ...], where m is the maximum
    score for the given subtask and t is the parameter for specifying
    testcases.

    If t is int, it is interpreted as the number of testcases
    comprising the subtask (that are consumed from the first to the
    last, sorted by num). If t is unicode, it is interpreted as the regular
    expression of the names of target testcases. All t must have the same type.

    A subclass must implement the method 'get_public_outcome' and
    'reduce'.

    """

    def retrieve_target_testcases(self) -> List[List[int]]:
        """Return the list of the target testcases for each subtask.

        Each element of the list consist of multiple strings.
        Each string represents the testcase name which should be included
        to the corresponding subtask.
        The order of the list is the same as 'parameters'.

        return ([[int]]): the list of the target testcases for each task.

        """

        t_params = [p[1] for p in self.parameters]

        if all(isinstance(t, int) for t in t_params):

            indices = list(range(self.n_input))
            current = 0
            targets = []

            for t in t_params:
                next_ = current + t
                targets.append(indices[current:next_])
                current = next_

            return targets

        raise ValueError(
            "In the score type parameters, the second value of each element "
            "must have the same type (int or unicode)")

    def max_scores(self) -> float:
        """See ScoreType.max_score."""
        score = 0.0

        for st_idx, parameter in enumerate(self.parameters):
            score += parameter[0]

        return score

    def compute_score(self, submission_result: SubmissionResult) -> Tuple[float, Any]:
        """See ScoreType.compute_score."""
        score = 0
        subtasks = []

        targets = self.retrieve_target_testcases()
        evaluations = {ev.codename: ev for ev in submission_result.evaluations}

        for st_idx, parameter in enumerate(self.parameters):
            target = targets[st_idx]

            testcases = []
            for tc_idx in target:
                tc_outcome = self.get_public_outcome(
                    float(evaluations[tc_idx].outcome), parameter)

                testcases.append({
                    "idx": tc_idx,
                    "outcome": tc_outcome,
                    "text": evaluations[tc_idx].text,
                    "time": evaluations[tc_idx].execution_time,
                    "memory": evaluations[tc_idx].execution_memory})

            st_score_fraction = self.reduce(
                [float(evaluations[tc_idx].outcome) for tc_idx in target],
                parameter)
            st_score = st_score_fraction * parameter[0]

            score += st_score
            subtasks.append({
                "idx": st_idx + 1,
                # We store the fraction so that an "example" testcase
                # with a max score of zero is still properly rendered as
                # correct or incorrect.
                "score_fraction": st_score_fraction,
                "max_score": parameter[0],
                "testcases": testcases})

        return score, subtasks

    @abstractmethod
    def get_public_outcome(self, unused_outcome, unused_parameter):
        """Return a public outcome from an outcome.

        The public outcome is shown to the user, and this method
        return the public outcome associated to the outcome of a
        submission in a testcase contained in the group identified by
        parameter.

        unused_outcome (float): the outcome of the submission in the
            testcase.
        unused_parameter (list): the parameters of the current group.

        return (str): the public output.

        """
        pass

    @abstractmethod
    def reduce(self, unused_outcomes, unused_parameter):
        """Return the score of a subtask given the outcomes.

        unused_outcomes ([float]): the outcomes of the submission in
            the testcases of the group.
        unused_parameter (list): the parameters of the group.

        return (float): the public output.

        """
        pass
