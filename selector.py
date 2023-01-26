import pandas as pd
import argparse
parser = argparse.ArgumentParser()


class Selector:
    def select_from_remaining(self, num_spaces):
        self.selection('remaining.csv', num_spaces)

    def selection(self, file_location, pre_approved_list, num_spaces):
        data = self._read_excel(file_location)

        data = self._filter_data(pre_approved_list, data)

        num_to_select = self._num_to_select(pre_approved_list, num_spaces, data)
        selected = self._select(num_to_select, data)

        self._write_remaining(data, selected)

        return list(selected.index), list(selected['Full Name (on your UCL Student Card)'])

    def _write_remaining(self, data, selected):
        remaining = data[~data.index.isin(selected.index)]
        remaining.to_csv('remaining.csv')

    def _select(self, num_spaces, data):
        selected = data.sample(n=num_spaces)[['Full Name (on your UCL Student Card)']]
        selected.to_csv('selected.csv')
        return selected

    def _num_to_select(self, pre_approved_list, num_spaces, data):
        return min(num_spaces - len(pre_approved_list), len(data))

    def _filter_data(self, pre_approved_list, data):
        pre_approved_mask = data['Full Name (on your UCL Student Card)'].isin(pre_approved_list)
        all_good_mask = (data[data.columns[4:]] == 'Yes').all(axis=1)
        is_member_mask = self._get_is_member_mask(data)
        selection_set = all_good_mask & ~pre_approved_mask & is_member_mask
        data = data[selection_set]
        return data

    def _read_excel(self, file_location):
        data = pd.read_excel(file_location)
        data = data.drop_duplicates('UCL Email Address')
        data = data.set_index('UCL Email Address')
        return data
    
    def _get_membership(self):
        members = pd.read_csv('membership.csv')
        full_member_mask = members['Membership type'] == 'Standard'
        full_members = members.loc[full_member_mask, ['Email', 'Full name']]
        return full_members
    
    def _get_is_member_mask(self, data):
        full_members = self._get_membership()

        member_names, member_email_names, member_emails = self._collect_member_details(full_members)
       
        data_names, data_emails = self._collect_data_names(data)
        
        return data_names.isin(member_names) | data_names.isin(member_email_names) | data_emails.isin(member_emails)

    def _collect_data_names(self, data):
        data_names = data['Full Name (on your UCL Student Card)'].str.lower().str.strip()
        data_names = data_names.str.split(' ').str[0] + ' ' + data_names.str.split(' ').str[-1]
        data_emails = data.index.str.strip().str.lower()
        return data_names,data_emails

    def _collect_member_details(self, full_members):
        member_names =  full_members['Full name'].str.split(' ').str[0].str.lower() + ' ' + full_members['Full name'].str.split(' ').str[-1].str.lower()
        member_email_names = full_members['Email'].str.split('.').str[0] + (' ' + full_members['Email'].str.split('.').str[1] if '@' not in full_members['Email'].str.split('.')[1] else '')
        member_emails = full_members['Email'].str.strip().str.lower()
        return member_names,member_email_names,member_emails

    

class SelectorDriver:
    def run(self):
        arguments = self._set_args()

        if arguments.number_spaces is None or (arguments.file_location is None and arguments.draw_remaining is None):
            emails, names = self._select_with_input()
        else:
            emails, names = self._select_with_args(arguments)

        print("Selected", len(names), "members")
        print("\nSelected Names:")
        print(*names, sep =', ')
        print("\nSelected Emails:")
        print(*emails, sep =', ')

    def _select_with_args(self, arguments):
        num_spaces = arguments.number_spaces
        pre_approved = arguments.preapproved.split(', ') if arguments.preapproved is not None else []
        if arguments.draw_remaining is None:
            file_location = arguments.file_location
            emails, names = Selector().selection(file_location, pre_approved, num_spaces)
        else:
            emails, names = Selector().select_from_remaining(num_spaces)
        return emails,names

    def _set_args(self):
        parser.add_argument("-n", "--number-spaces", help="Number of spaces avalible", type=int)
        parser.add_argument("-r", "--draw-remaining", help="Draw from the list of remaining users")
        parser.add_argument("-f", "--file-location", help="Location of file to draw from")
        parser.add_argument("-p", "--preapproved", help="List of pre-approved names")
        arguments = parser.parse_args()
        return arguments

    def _select_with_input(self):
        num_spaces = int(input("Number of spaces: "))
        use_remaining = input("Draw from remaining? (Y/N): ")
        pre_approved = input("Enter pre-approved names (alice, bob, jim): ").split(', ')
        if use_remaining[0] == 'Y' or use_remaining[0] == 'y':
            emails, names = Selector().select_from_remaining(num_spaces)
        else:
            file_location = input("Enter file location of responses: ")
            emails, names = Selector().selection(file_location, pre_approved, num_spaces)
        return emails,names


if __name__ == '__main__':
    SelectorDriver().run()
