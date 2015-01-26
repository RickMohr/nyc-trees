class FilterModule(object):
    ''' Additional filters for use within Ansible. '''

    def filters(self):
        return {
            'is_not_in': self.is_not_in,
            'is_in': self.is_in,
            'some_are_in': self.some_are_in
        }

    def is_not_in(self, *t):
        """Determnies if there are no elements in common between x and y

            x | is_not_in(y)

        Arguments
        :param t: A tuple with two elements (x and y)
        """
        groups_to_test, all_group_names = t

        return set(groups_to_test).isdisjoint(set(all_group_names))

    def is_in(self, *t):
        """Determnies if all of the elements in x are a subset of y

            x | is_in(y)

        Arguments
        :param t: A tuple with two elements (x and y)
        """
        groups_to_test, all_group_names = t

        return set(groups_to_test).issubset(set(all_group_names))

    def some_are_in(self, *t):
        """Determnies if any element in x intersects with y

            x | some_are_in(y)

        Arguments
        :param t: A tuple with two elements (x and y)
        """
        groups_to_test, all_group_names = t

        return len(set(groups_to_test) & set(all_group_names)) > 0
