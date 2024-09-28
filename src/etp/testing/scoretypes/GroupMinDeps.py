from etp.testing.scoretypes.GroupMin import GroupMin


class GroupMinDeps(GroupMin):
    """The score of a submission is the sum of the minimums of
    group scores. Additionally, every group may list a number of
    dependencies; in that case, points are awarded for that group
    only if the submission gets a nonzero score in each dependency.

    More specifically, for each group, its score_fraction AFTER is set to 0
    if, for any dependency, its score_fraction BEFORE was 0. No 'transitive
    closure' is calculated, you should recursively list all dependencies of
    dependencies manually if such behavior is desired.

    Parameters are [[m, t, p1, p2, ...], ... ]. See ScoreTypeGroup for m
    and t. p1, p2, ... can be strings of the form 'key:value'. This class
    recognizes two types of parameters:
     - name:group_name
     - deps:group1,group2,group3

    """

    @staticmethod
    def parse_parameters(parameters):
        parsed = {}
        # first 2 are points and number of testcases
        for kv in parameters[2:]:
            if ":" not in kv:
                continue

            key, value = kv.split(":", 1)
            if key == "deps":
                parsed[key] = value.split(",")
            else:
                parsed[key] = value

        if "name" not in parsed:
            parsed["name"] = None
        if "deps" not in parsed:
            parsed["deps"] = []
        return parsed

    def compute_score(self, submission_result):
        score, subtasks = GroupMin.compute_score(self, submission_result)
        if len(subtasks) == len(self.parameters):
            passed_subtasks = set()
            for st_idx, parameter in enumerate(self.parameters):
                name = self.parse_parameters(parameter)["name"]
                if bool(name) and subtasks[st_idx]["score_fraction"] > 0:
                    passed_subtasks.add(name)
            for st_idx, parameter in enumerate(self.parameters):
                failed_deps = False
                deps = self.parse_parameters(parameter)["deps"]

                for dep in deps:
                    if dep not in passed_subtasks:
                        failed_deps = True

                if failed_deps:
                    st_score = subtasks[st_idx]["score_fraction"] * parameter[0]
                    score -= st_score
                    subtasks[st_idx]["score_ignore"] = True
                    # set score_fraction to 0 too to avoid max_subtask undoing our work here...
                    subtasks[st_idx]["score_fraction"] = 0.0
        return score, subtasks
